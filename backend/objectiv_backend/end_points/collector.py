import json
from datetime import datetime

import flask
import time
from typing import List
import uuid

from flask import Response, Request

from objectiv_backend.common.config import get_collector_config
from objectiv_backend.common.db import get_db_connection
from objectiv_backend.common.event_utils import event_add_construct_context, add_global_context_to_event
from objectiv_backend.common.types import EventWithId, EventData, ContextData
from objectiv_backend.end_points.common import get_json_response, get_cookie_id
from objectiv_backend.end_points.extra_output import events_to_json, write_data_to_fs_if_configured, \
    write_data_to_s3_if_configured
from objectiv_backend.schema.validate_events import validate_structure_event_list, EventError
from objectiv_backend.workers.pg_queues import PostgresQueues, ProcessingStage
from objectiv_backend.workers.pg_storage import insert_events_into_nok_data
from objectiv_backend.workers.worker_entry import process_events_entry
from objectiv_backend.workers.worker_finalize import insert_events_into_data


# Some limits on the inputs we accept
DATA_MAX_SIZE_BYTES = 1_000_000
DATA_MAX_EVENT_COUNT = 1_000


def collect() -> Response:
    """
    Endpoint that accepts event data from the tracker and stores it for further processing.
    """
    current_millis = round(time.time() * 1000)
    try:
        events = _get_event_data(flask.request)
    except ValueError as exc:
        print(f'Data problem: {exc}')  # todo: real error logging

        return _get_collector_response(error_count=1, event_count=-1, data_error=exc.__str__())

    # Do all the enrichment steps that can only be done in this phase
    add_http_contexts(events)
    add_cookie_id_contexts(events)
    set_time_in_events(events, current_millis)

    """
    Map event data to a list of EventWithId entities.
    Event data has been validated against the schema in the _get_event_data above. So all Events will have an `id`. 
    """
    events_with_id = [EventWithId(id=uuid.UUID(event.get('id')), event=event) for event in events]

    if not get_collector_config().async_mode:
        ok_events, nok_events, event_errors = process_events_entry(events=events_with_id, current_millis=current_millis)
        print(f'ok_events: {len(ok_events)}, nok_events: {len(nok_events)}')
        write_sync_events(ok_events=ok_events, nok_events=nok_events)
        return _get_collector_response(error_count=len(nok_events), event_count=len(events), event_errors=event_errors)
    else:
        write_async_events(events=events_with_id)
        return _get_collector_response(error_count=0, event_count=len(events))


def _get_event_data(request: Request) -> List[EventData]:
    """
    Parse the requests data as json and return as a list

    :raise ValueError:
        1) data is not valid json
        2) data is bigger than DATA_MAX_SIZE_BYTES
        3) The parsed data is a list with more than DATA_MAX_EVENT_COUNT entries
        4) The parsed data is not a list, as expected
        5) The parsed data is not structured as a list of events. This only does basic validation, see
            the validate_structure_data function for more information
    :param request: Request from which to parse the data
    :return: the parsed data, a list of EventData
    """
    post_data = request.data
    if len(post_data) > DATA_MAX_SIZE_BYTES:
        # if it's more than a megabyte, we'll refuse to process
        raise ValueError(f'Data size exceeds limit')
    events = json.loads(post_data)
    if not isinstance(events, list):
        raise ValueError('Parsed data is not a list')
    if len(events) > DATA_MAX_EVENT_COUNT:
        raise ValueError('Events exceeds limit')
    error_info = validate_structure_event_list(event_data=events)
    if error_info:
        raise ValueError(f'List of Events not structured well: {error_info[0].info}')
    return events


def _get_collector_response(
        error_count: int, event_count: int, event_errors: List[EventError] = None, data_error: str = '') -> Response:
    """
    Create a Response object, with a json message with event counts, and a cookie set if needed.
    """

    if not get_collector_config().error_reporting:
        event_errors = []
        data_error = ''
    else:
        if event_errors is None:
            event_errors = []

    status = 200 if error_count == 0 else 400
    msg = json.dumps({
        "status": f"{status}",
        "error_count": error_count,
        "event_count": event_count,
        "event_errors": event_errors,
        "data_error": data_error
    })
    return get_json_response(status=status, msg=msg)


def add_http_contexts(events: List[EventData]):
    """
    Modify the given list of events: Add the HttpContext to each event
    """
    # get http context for current request (same for all events in this request)
    http_context = _get_http_context()
    for event in events:
        add_global_context_to_event(event=event, context=http_context)


def add_cookie_id_contexts(events: List[EventData]):
    """
    Modify the given list of events: Add the CookieIdContext to each event, if cookies are enabled.
    """
    cookie_config = get_collector_config().cookie
    if not cookie_config:
        return
    cookie_id = get_cookie_id()
    for event in events:
        event_add_construct_context(
            event=event,
            context_type='CookieIdContext',
            context_id=cookie_id,
            cookie_id=cookie_id
        )


def set_time_in_events(events: List[EventData], current_millis: int):
    """
    Modify the given list of events: Set the correct time in the events

    Adjust time if needed: if the current requests header has an X-timestamp header, we'll use that to
    calculate the client's clock skew, and adjust all events in the list.
    :param events: List of events to modify
    :param current_millis: time in milliseconds since epoch UTC, when this request was received.
    """
    offset = 0
    # transport_time is the same for all events in one batch
    # so we use the transport_time from the first event
    if 'transport_time' in events[0]:
        try:
            client_millis = int(events[0]['transport_time'])
        except ValueError as exc:
            client_millis = current_millis
        offset = current_millis - client_millis
        print(f'debug - time offset: {offset}')
    for event in events:
        # here we correct the tracking time with the calculated offset
        # the assumption here is that transport time should be the same as the server time (current_millis)
        # to account for clients that have an out-of-sync clock
        event['time'] = event['tracking_time'] + offset

        # remove unwanted timestamps
        del event['tracking_time']
        del event['transport_time']


def _get_http_context() -> ContextData:
    """ Create an HttpContext based on the data in the current request. """
    allowed_headers = ['Host', 'Origin', 'Referer', 'User-Agent']
    http_context: ContextData = {}
    if flask.request.remote_addr:
        http_context['remote_address'] = flask.request.remote_addr

    for h, v in flask.request.headers.items():
        if h in allowed_headers:
            if h == 'User-Agent':
                http_context['user_agent'] = v
            else:
                http_context[h.lower()] = v

    http_context['_context_type'] = 'HttpContext'
    http_context['id'] = 'http_context'
    return http_context


def write_sync_events(ok_events: List[EventWithId], nok_events: List[EventWithId]):
    """
    Write the events to the following sinks, if configured:
        * postgres
        * aws
        * file system
    """
    output_config = get_collector_config().output
    # todo: add exception handling. if one output fails, continue to next if configured.
    if output_config.postgres:
        connection = get_db_connection(output_config.postgres)
        try:
            with connection:
                insert_events_into_data(connection, events=ok_events)
                insert_events_into_nok_data(connection, events=nok_events)
        finally:
            connection.close()

    if not output_config.file_system and not output_config.aws:
        return
    for prefix, events in ('OK', ok_events), ('NOK', nok_events):
        if events:
            data = events_to_json(events)
            moment = datetime.utcnow()
            write_data_to_fs_if_configured(data=data, prefix=prefix, moment=moment)
            write_data_to_s3_if_configured(data=data, prefix=prefix, moment=moment)


def write_async_events(events: List[EventWithId]):
    """
    Write the events to the following sinks, if configured:
        * postgres - To the entry queue
        * aws - to the 'RAW' prefix
        * file system - to the 'RAW' directory
    """
    output_config = get_collector_config().output
    # todo: add exception handling. if one output fails, continue to next if configured.
    if output_config.postgres:
        connection = get_db_connection(output_config.postgres)
        try:
            with connection:
                pg_queue = PostgresQueues(connection=connection)
                pg_queue.put_events(queue=ProcessingStage.ENTRY, events=events)
        finally:
            connection.close()

    if not output_config.file_system and not output_config.aws:
        return
    prefix = 'RAW'
    if events:
        data = events_to_json(events)
        moment = datetime.utcnow()
        write_data_to_fs_if_configured(data=data, prefix=prefix, moment=moment)
        write_data_to_s3_if_configured(data=data, prefix=prefix, moment=moment)

