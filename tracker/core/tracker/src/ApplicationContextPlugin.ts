import { ApplicationContext } from '@objectiv/schema';
import { makeApplicationContext } from './ContextFactories';
import { TrackerConfig, TrackerConsole } from './Tracker';
import { TrackerEvent } from './TrackerEvent';
import { TrackerPlugin, TrackerPluginConfig } from './TrackerPlugin';

/**
 * The ApplicationContextPlugin Config object.
 */
export type ApplicationContextPluginConfig = TrackerPluginConfig & Pick<TrackerConfig, 'applicationId'>;

/**
 * The ApplicationContext Plugin adds an ApplicationContext as GlobalContext before events are transported.
 */
export class ApplicationContextPlugin implements TrackerPlugin {
  readonly console?: TrackerConsole;
  readonly pluginName = `ApplicationContextPlugin`;
  readonly applicationContext: ApplicationContext;

  /**
   * Generates a ApplicationContext from the given config applicationId.
   */
  constructor(config: ApplicationContextPluginConfig) {
    this.console = config.console;
    this.applicationContext = makeApplicationContext({
      id: config.applicationId,
    });

    if (this.console) {
      this.console.groupCollapsed(`｢objectiv:${this.pluginName}｣ Initialized`);
      this.console.log(`Application ID: ${config.applicationId}`);
      this.console.group(`Application Context:`);
      this.console.log(this.applicationContext);
      this.console.groupEnd();
      this.console.groupEnd();
    }
  }

  /**
   * Add the the ApplicationContext to the Event's Global Contexts
   */
  beforeTransport(event: TrackerEvent): void {
    event.global_contexts.push(this.applicationContext);
  }

  /**
   * Make this plugin usable only if the Navigator API is available
   */
  isUsable(): boolean {
    return true;
  }
}
