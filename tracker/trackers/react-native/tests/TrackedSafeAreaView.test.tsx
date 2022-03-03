/*
 * Copyright 2022 Objectiv B.V.
 */

import { mockConsole, SpyTransport } from '@objectiv/testing-tools';
import { getLocationPath } from '@objectiv/tracker-core';
import { render } from '@testing-library/react-native';
import React from 'react';
import { Text } from 'react-native';
import {
  LocationTree,
  ReactTracker,
  RootLocationContextWrapper,
  TrackedSafeAreaView,
  TrackedSafeAreaViewProps,
  TrackingContextProvider,
  useLocationStack,
} from '../src';

describe('TrackedSafeAreaView', () => {
  const spyTransport = new SpyTransport();
  jest.spyOn(spyTransport, 'handle');
  const tracker = new ReactTracker({ applicationId: 'app-id', transport: spyTransport, console: mockConsole });
  jest.spyOn(console, 'debug').mockImplementation(jest.fn);

  const TestTrackedSafeAreaView = (props: TrackedSafeAreaViewProps & { testID?: string }) => (
    <TrackingContextProvider tracker={tracker}>
      <RootLocationContextWrapper id={'test'}>
        <TrackedSafeAreaView {...props} />
      </RootLocationContextWrapper>
    </TrackingContextProvider>
  );

  beforeEach(() => {
    jest.resetAllMocks();
    LocationTree.clear();
  });

  const SafeAreaViewChild = (props: { title: string }) => {
    const locationPath = getLocationPath(useLocationStack());

    console.debug(locationPath);

    return (
      <Text>
        {props.title}:{locationPath}
      </Text>
    );
  };

  it('should wrap SafeAreaView in ContentContext', () => {
    render(
      <TestTrackedSafeAreaView id={'test-safe-area-view'}>
        <SafeAreaViewChild title={'Child'} />
      </TestTrackedSafeAreaView>
    );

    expect(console.debug).toHaveBeenCalledTimes(1);
    expect(console.debug).toHaveBeenNthCalledWith(1, 'RootLocation:test / Content:test-safe-area-view');
  });
});
