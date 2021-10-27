import { LocationStack } from '@objectiv/tracker-core';
import { BrowserTracker, TaggableElement } from '../';
import { parseLocationContext } from '../structs';
import { TaggingAttribute } from '../TaggingAttribute';
import { trackerErrorHandler } from '../trackerErrorHandler';
import { isTaggableElement } from '../typeGuards';
import { findTaggedParentElements } from './findTaggedParentElements';

/**
 * Generates a location stack for the given Element. If a Tracker instance is provided, also predicts its mutations.
 *
 * 1. Traverses the DOM to reconstruct the component stack
 * 2. If a Tracker instance is provided, retrieves the Tracker's Location Stack
 * 3. Merges the two Location Stacks to reconstruct the full Location
 * 4. If a Tracker instance is provided, runs the Tracker's plugins `beforeTransport` lifecycle on the locationStack
 */
export const getElementLocationStack = (parameters: {
  element: TaggableElement | EventTarget;
  tracker?: BrowserTracker;
}) => {
  const locationStack: LocationStack = [];

  try {
    const { element, tracker } = parameters;

    // Add Tracker's location to the locationStack
    if (tracker) {
      locationStack.push(...tracker.location_stack);
    }

    // Traverse the DOM to reconstruct Element's Location
    if (isTaggableElement(element)) {
      // Retrieve parent Tracked Elements
      const elementsStack = findTaggedParentElements(element).reverse();

      // Re-hydrate Location Stack
      elementsStack.forEach((element) => {
        // Get, parse, validate, hydrate and push Location Context in the Location Stack
        locationStack.push(parseLocationContext(element.getAttribute(TaggingAttribute.context)));
      });
    }

    // Add Plugins mutations to the locationStack - global_contexts are not a concern, so we pass an empty array
    if (tracker) {
      tracker.plugins.beforeTransport({ location_stack: locationStack, global_contexts: [] });
    }
  } catch (error) {
    trackerErrorHandler(error, parameters);
  }

  return locationStack;
};
