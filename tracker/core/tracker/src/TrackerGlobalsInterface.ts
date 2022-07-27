/*
 * Copyright 2022 Objectiv B.V.
 */

import { TrackerDeveloperToolsInterface } from './TrackerDeveloperToolsInterface';
import { TrackerRepositoryInterface } from './TrackerRepositoryInterface';

/**
 * Globals interface definition.
 */
export interface TrackerGlobalsInterface {
  devTools?: TrackerDeveloperToolsInterface;
  TrackerRepository: TrackerRepositoryInterface<any>;
  versions: Map<string, string>;
}
