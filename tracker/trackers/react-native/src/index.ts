/*
 * Copyright 2022 Objectiv B.V.
 */

/**
 * Set package version in globals
 */
import pkg from '../package.json';
globalThis.objectiv = globalThis.objectiv ?? {};
globalThis.objectiv.versions = globalThis.objectiv.versions ?? new Map();
globalThis.objectiv.versions.set(pkg.name, pkg.version);

import 'react-native-get-random-values';

export * from '@objectiv/tracker-react-core';

export * from './common/factories/makeReactNativeTrackerDefaultPluginsList';
export * from './common/factories/makeReactNativeTrackerDefaultQueue';
export * from './common/factories/makeReactNativeTrackerDefaultTransport';

export * from './trackedComponents/TrackedActivityIndicator';
export * from './trackedComponents/TrackedButton';
export * from './trackedComponents/TrackedFlatList';
export * from './trackedComponents/TrackedKeyboardAvoidingView';
export * from './trackedComponents/TrackedModal';
export * from './trackedComponents/TrackedPressable';
export * from './trackedComponents/TrackedSafeAreaView';
export * from './trackedComponents/TrackedScrollView';
export * from './trackedComponents/TrackedSectionList';
export * from './trackedComponents/TrackedSwitch';
export * from './trackedComponents/TrackedText';
export * from './trackedComponents/TrackedTextInput';
export * from './trackedComponents/TrackedTouchableHighlight';
export * from './trackedComponents/TrackedTouchableNativeFeedback';
export * from './trackedComponents/TrackedTouchableOpacity';
export * from './trackedComponents/TrackedTouchableWithoutFeedback';
export * from './trackedComponents/TrackedView';
export * from './trackedComponents/TrackedVirtualizedList';

export * from './ReactNativeTracker';
