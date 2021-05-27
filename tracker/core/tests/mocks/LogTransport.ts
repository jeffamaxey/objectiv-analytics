import { TrackerTransport } from '../../src';

export class LogTransport implements TrackerTransport {
  handle(): void {
    console.log('LogTransport.handle');
  }

  isUsable(): boolean {
    return true;
  }
}
