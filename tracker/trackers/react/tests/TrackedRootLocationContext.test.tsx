/*
 * Copyright 2022 Objectiv B.V.
 */

import { MockConsoleImplementation, SpyTransport } from '@objectiv/testing-tools';
import { LocationContextName, TrackerRepository } from '@objectiv/tracker-core';
import { fireEvent, getByText, render, screen } from '@testing-library/react';
import React, { createRef } from 'react';
import { ObjectivProvider, ReactTracker, TrackedRootLocationContext, usePressEventTracker } from '../src';

require('@objectiv/developer-tools');
globalThis.objectiv?.TrackerConsole.setImplementation(MockConsoleImplementation);

describe('TrackedRootLocationContext', () => {
  beforeEach(() => {
    jest.resetAllMocks();
    TrackerRepository.trackersMap.clear();
    TrackerRepository.defaultTracker = undefined;
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should wrap the given Component in a RootLocationContext', () => {
    const spyTransport = new SpyTransport();
    jest.spyOn(spyTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: spyTransport });

    const TrackedButton = () => {
      const trackPressEvent = usePressEventTracker();
      return <div onClick={trackPressEvent}>Trigger Event</div>;
    };

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedRootLocationContext Component={'div'} id={'root-id'}>
          <TrackedButton />
        </TrackedRootLocationContext>
      </ObjectivProvider>
    );

    fireEvent.click(getByText(container, /trigger event/i));

    expect(spyTransport.handle).toHaveBeenCalledTimes(2);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'ApplicationLoadedEvent',
      })
    );
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.RootLocationContext,
            id: 'root-id',
          }),
        ]),
      })
    );
  });

  it('should allow disabling id normalization', () => {
    const spyTransport = new SpyTransport();
    jest.spyOn(spyTransport, 'handle');
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: spyTransport });

    const TrackedButton = ({ children }: { children: React.ReactNode }) => {
      const trackPressEvent = usePressEventTracker();
      return <div onClick={trackPressEvent}>{children}</div>;
    };

    const { container } = render(
      <ObjectivProvider tracker={tracker}>
        <TrackedRootLocationContext Component={'div'} id={'Root id 1'}>
          <TrackedButton>Trigger Event 1</TrackedButton>
        </TrackedRootLocationContext>
        <TrackedRootLocationContext Component={'div'} id={'Root id 2'} normalizeId={false}>
          <TrackedButton>Trigger Event 2</TrackedButton>
        </TrackedRootLocationContext>
      </ObjectivProvider>
    );

    fireEvent.click(getByText(container, /trigger event 1/i));
    fireEvent.click(getByText(container, /trigger event 2/i));

    expect(spyTransport.handle).toHaveBeenCalledTimes(3);
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      1,
      expect.objectContaining({
        _type: 'ApplicationLoadedEvent',
      })
    );
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      2,
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.RootLocationContext,
            id: 'root-id-1',
          }),
        ]),
      })
    );
    expect(spyTransport.handle).toHaveBeenNthCalledWith(
      3,
      expect.objectContaining({
        _type: 'PressEvent',
        location_stack: expect.arrayContaining([
          expect.objectContaining({
            _type: LocationContextName.RootLocationContext,
            id: 'Root id 2',
          }),
        ]),
      })
    );
  });

  it('should console.error if an id cannot be automatically generated', () => {
    jest.spyOn(console, 'error').mockImplementation(() => {});
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new SpyTransport() });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedRootLocationContext Component={'div'} id={'☹️'} />
      </ObjectivProvider>
    );

    expect(MockConsoleImplementation.error).toHaveBeenCalledTimes(1);
    expect(MockConsoleImplementation.error).toHaveBeenCalledWith(
      '｢objectiv｣ Could not generate a valid id for RootLocationContext. Please provide the `id` property.'
    );
  });

  it('should allow forwarding the id property', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new SpyTransport() });

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedRootLocationContext Component={'div'} id={'root-id-1'} data-testid={'test-root-1'}>
          test
        </TrackedRootLocationContext>
        <TrackedRootLocationContext Component={'div'} id={'root-id-2'} forwardId={true} data-testid={'test-root-2'}>
          test
        </TrackedRootLocationContext>
      </ObjectivProvider>
    );

    expect(screen.getByTestId('test-root-1').getAttribute('id')).toBe(null);
    expect(screen.getByTestId('test-root-2').getAttribute('id')).toBe('root-id-2');
  });

  it('should allow forwarding refs', () => {
    const tracker = new ReactTracker({ applicationId: 'app-id', transport: new SpyTransport() });
    const ref = createRef<HTMLDivElement>();

    render(
      <ObjectivProvider tracker={tracker}>
        <TrackedRootLocationContext Component={'div'} id={'root-id'} ref={ref}>
          test
        </TrackedRootLocationContext>
      </ObjectivProvider>
    );

    expect(ref.current).toMatchInlineSnapshot(`
      <div>
        test
      </div>
    `);
  });
});
