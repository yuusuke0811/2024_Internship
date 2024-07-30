import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';
import { webSocket } from "rxjs/webSocket";

@Injectable({
  providedIn: 'root'
})

/**
 * Websocketサービスクラス
 */
export class WebsocketService {
public ImageData: any;
  /**
   * コンストラクタ
   */
  constructor() { }

  connect(host: string, port: string): Subject<string> {
    return webSocket({
      url: `ws://${ host }:${ port }`,
      deserializer: ({ data }) => data
    })
  }
}
