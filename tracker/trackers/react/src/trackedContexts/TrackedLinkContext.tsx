/*
 * Copyright 2021-2022 Objectiv B.V.
 */

import { getLocationPath, makeIdFromString } from '@objectiv/tracker-core';
import React from 'react';
import { makeTitleFromChildren } from '../common/factories/makeTitleFromChildren';
import { trackPressEvent } from '../eventTrackers/trackPressEvent';
import { useLocationStack } from '../hooks/consumers/useLocationStack';
import { LinkContextWrapper } from '../locationWrappers/LinkContextWrapper';
import { TrackedPressableContextProps } from '../types';

/**
 * The props of TrackedLinkContext. Extends TrackedPressableProps with the `href` property.
 */
export type TrackedLinkContextProps = TrackedPressableContextProps & {
  /**
   * The destination url.
   */
  href: string;

  /**
   * Whether to forward the given href to the given Component.
   */
  forwardHref?: boolean;

  /**
   * Whether to block and wait for the Tracker having sent the event. Eg: a button redirecting to a new location.
   */
  waitUntilTracked?: boolean;
};

/**
 * Generates a new React Element already wrapped in an LinkContext.
 * Automatically tracks PressEvent when the given Component receives an `onClick` SyntheticEvent.
 */
export const TrackedLinkContext = React.forwardRef<HTMLElement, TrackedLinkContextProps>((props, ref) => {
  const {
    Component,
    id,
    title,
    href,
    forwardId = false,
    forwardTitle = false,
    forwardHref = false,
    waitUntilTracked = false,
    ...otherProps
  } = props;

  const linkTitle = title ?? makeTitleFromChildren(props.children);

  const linkId = id ?? makeIdFromString(linkTitle);

  const componentProps = {
    ...otherProps,
    ...(ref ? { ref } : {}),
    ...(forwardId ? { id } : {}),
    ...(forwardTitle ? { title } : {}),
    ...(forwardHref ? { href } : {}),
  };

  const locationPath = getLocationPath(useLocationStack());
  if (!linkId) {
    console.error(
      `｢objectiv｣ Could not generate a valid id for LinkContext @ ${locationPath}. Please provide either the \`title\` or the \`id\` property manually.`
    );
    return React.createElement(Component, componentProps);
  }

  return (
    <LinkContextWrapper id={linkId} href={href}>
      {(trackingContext) =>
        React.createElement(Component, {
          ...componentProps,
          onClick: async (event) => {
            if (!waitUntilTracked) {
              // Track PressEvent: non-blocking.
              trackPressEvent(trackingContext);

              // Execute onClick prop, if any.
              props.onClick && props.onClick(event);
            } else {
              // Prevent event from being handled by the user agent.
              event.preventDefault();

              // Track PressEvent: best-effort blocking.
              await trackPressEvent({
                ...trackingContext,
                options: {
                  // Best-effort: wait for Queue to be empty. Times out to max 1s on very slow networks.
                  waitForQueue: true,
                  // Regardless whether waiting resulted in PressEvent being tracked, flush the Queue.
                  flushQueue: true,
                },
              });

              // Execute onClick prop, if any.
              props.onClick && props.onClick(event);

              // Resume navigation.
              window.location.href = href;
            }
          },
        })
      }
    </LinkContextWrapper>
  );
});
