/*
   Licensed to the Apache Software Foundation (ASF) under one or more
   contributor license agreements.  See the NOTICE file distributed with
   this work for additional information regarding copyright ownership.
   The ASF licenses this file to You under the Apache License, Version 2.0
   (the "License"); you may not use this file except in compliance with
   the License.  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
$(document).ready(function() {

    $(".click-title").mouseenter( function(    e){
        e.preventDefault();
        this.style.cursor="pointer";
    });
    $(".click-title").mousedown( function(event){
        event.preventDefault();
    });

    // Ugly code while this script is shared among several pages
    try{
        refreshHitsPerSecond(true);
    } catch(e){}
    try{
        refreshResponseTimeOverTime(true);
    } catch(e){}
    try{
        refreshResponseTimePercentiles();
    } catch(e){}
});


var responseTimePercentilesInfos = {
        data: {"result": {"minY": 20.0, "minX": 0.0, "maxY": 755.0, "series": [{"data": [[0.0, 20.0], [0.1, 32.0], [0.2, 46.0], [0.3, 46.0], [0.4, 50.0], [0.5, 57.0], [0.6, 60.0], [0.7, 62.0], [0.8, 98.0], [0.9, 99.0], [1.0, 118.0], [1.1, 160.0], [1.2, 166.0], [1.3, 175.0], [1.4, 175.0], [1.5, 177.0], [1.6, 181.0], [1.7, 183.0], [1.8, 190.0], [1.9, 193.0], [2.0, 202.0], [2.1, 222.0], [2.2, 228.0], [2.3, 236.0], [2.4, 254.0], [2.5, 257.0], [2.6, 260.0], [2.7, 263.0], [2.8, 269.0], [2.9, 269.0], [3.0, 272.0], [3.1, 274.0], [3.2, 275.0], [3.3, 276.0], [3.4, 278.0], [3.5, 281.0], [3.6, 282.0], [3.7, 282.0], [3.8, 284.0], [3.9, 285.0], [4.0, 286.0], [4.1, 287.0], [4.2, 288.0], [4.3, 288.0], [4.4, 289.0], [4.5, 290.0], [4.6, 290.0], [4.7, 291.0], [4.8, 291.0], [4.9, 292.0], [5.0, 292.0], [5.1, 293.0], [5.2, 293.0], [5.3, 293.0], [5.4, 294.0], [5.5, 294.0], [5.6, 295.0], [5.7, 295.0], [5.8, 296.0], [5.9, 296.0], [6.0, 296.0], [6.1, 297.0], [6.2, 298.0], [6.3, 298.0], [6.4, 299.0], [6.5, 299.0], [6.6, 299.0], [6.7, 301.0], [6.8, 301.0], [6.9, 301.0], [7.0, 302.0], [7.1, 302.0], [7.2, 302.0], [7.3, 303.0], [7.4, 303.0], [7.5, 304.0], [7.6, 304.0], [7.7, 304.0], [7.8, 305.0], [7.9, 305.0], [8.0, 306.0], [8.1, 307.0], [8.2, 307.0], [8.3, 308.0], [8.4, 309.0], [8.5, 310.0], [8.6, 311.0], [8.7, 311.0], [8.8, 311.0], [8.9, 312.0], [9.0, 313.0], [9.1, 313.0], [9.2, 315.0], [9.3, 315.0], [9.4, 316.0], [9.5, 316.0], [9.6, 317.0], [9.7, 318.0], [9.8, 318.0], [9.9, 319.0], [10.0, 319.0], [10.1, 320.0], [10.2, 320.0], [10.3, 322.0], [10.4, 322.0], [10.5, 323.0], [10.6, 324.0], [10.7, 324.0], [10.8, 324.0], [10.9, 324.0], [11.0, 324.0], [11.1, 325.0], [11.2, 325.0], [11.3, 327.0], [11.4, 327.0], [11.5, 327.0], [11.6, 328.0], [11.7, 329.0], [11.8, 330.0], [11.9, 331.0], [12.0, 332.0], [12.1, 332.0], [12.2, 332.0], [12.3, 334.0], [12.4, 336.0], [12.5, 336.0], [12.6, 337.0], [12.7, 339.0], [12.8, 339.0], [12.9, 340.0], [13.0, 341.0], [13.1, 342.0], [13.2, 342.0], [13.3, 343.0], [13.4, 344.0], [13.5, 344.0], [13.6, 346.0], [13.7, 348.0], [13.8, 350.0], [13.9, 350.0], [14.0, 351.0], [14.1, 351.0], [14.2, 352.0], [14.3, 352.0], [14.4, 354.0], [14.5, 357.0], [14.6, 357.0], [14.7, 359.0], [14.8, 361.0], [14.9, 362.0], [15.0, 362.0], [15.1, 363.0], [15.2, 363.0], [15.3, 364.0], [15.4, 364.0], [15.5, 364.0], [15.6, 365.0], [15.7, 365.0], [15.8, 365.0], [15.9, 365.0], [16.0, 366.0], [16.1, 366.0], [16.2, 366.0], [16.3, 366.0], [16.4, 367.0], [16.5, 368.0], [16.6, 368.0], [16.7, 368.0], [16.8, 368.0], [16.9, 369.0], [17.0, 370.0], [17.1, 370.0], [17.2, 370.0], [17.3, 370.0], [17.4, 371.0], [17.5, 371.0], [17.6, 372.0], [17.7, 372.0], [17.8, 372.0], [17.9, 372.0], [18.0, 373.0], [18.1, 373.0], [18.2, 373.0], [18.3, 373.0], [18.4, 373.0], [18.5, 374.0], [18.6, 374.0], [18.7, 374.0], [18.8, 374.0], [18.9, 374.0], [19.0, 374.0], [19.1, 374.0], [19.2, 374.0], [19.3, 375.0], [19.4, 375.0], [19.5, 375.0], [19.6, 375.0], [19.7, 376.0], [19.8, 376.0], [19.9, 376.0], [20.0, 376.0], [20.1, 377.0], [20.2, 377.0], [20.3, 377.0], [20.4, 377.0], [20.5, 377.0], [20.6, 377.0], [20.7, 377.0], [20.8, 377.0], [20.9, 377.0], [21.0, 378.0], [21.1, 378.0], [21.2, 378.0], [21.3, 378.0], [21.4, 378.0], [21.5, 378.0], [21.6, 378.0], [21.7, 378.0], [21.8, 378.0], [21.9, 378.0], [22.0, 379.0], [22.1, 379.0], [22.2, 379.0], [22.3, 379.0], [22.4, 379.0], [22.5, 379.0], [22.6, 379.0], [22.7, 379.0], [22.8, 380.0], [22.9, 380.0], [23.0, 380.0], [23.1, 380.0], [23.2, 380.0], [23.3, 380.0], [23.4, 380.0], [23.5, 380.0], [23.6, 381.0], [23.7, 381.0], [23.8, 381.0], [23.9, 381.0], [24.0, 381.0], [24.1, 381.0], [24.2, 381.0], [24.3, 381.0], [24.4, 381.0], [24.5, 382.0], [24.6, 382.0], [24.7, 382.0], [24.8, 382.0], [24.9, 382.0], [25.0, 382.0], [25.1, 382.0], [25.2, 382.0], [25.3, 382.0], [25.4, 383.0], [25.5, 383.0], [25.6, 383.0], [25.7, 383.0], [25.8, 383.0], [25.9, 383.0], [26.0, 383.0], [26.1, 383.0], [26.2, 383.0], [26.3, 383.0], [26.4, 383.0], [26.5, 383.0], [26.6, 383.0], [26.7, 383.0], [26.8, 384.0], [26.9, 384.0], [27.0, 384.0], [27.1, 384.0], [27.2, 384.0], [27.3, 384.0], [27.4, 384.0], [27.5, 384.0], [27.6, 384.0], [27.7, 384.0], [27.8, 384.0], [27.9, 385.0], [28.0, 385.0], [28.1, 385.0], [28.2, 385.0], [28.3, 385.0], [28.4, 385.0], [28.5, 385.0], [28.6, 385.0], [28.7, 385.0], [28.8, 385.0], [28.9, 386.0], [29.0, 386.0], [29.1, 386.0], [29.2, 386.0], [29.3, 386.0], [29.4, 386.0], [29.5, 386.0], [29.6, 387.0], [29.7, 387.0], [29.8, 387.0], [29.9, 387.0], [30.0, 387.0], [30.1, 387.0], [30.2, 387.0], [30.3, 387.0], [30.4, 387.0], [30.5, 387.0], [30.6, 387.0], [30.7, 387.0], [30.8, 387.0], [30.9, 388.0], [31.0, 388.0], [31.1, 388.0], [31.2, 388.0], [31.3, 388.0], [31.4, 388.0], [31.5, 388.0], [31.6, 388.0], [31.7, 388.0], [31.8, 388.0], [31.9, 388.0], [32.0, 389.0], [32.1, 389.0], [32.2, 389.0], [32.3, 389.0], [32.4, 389.0], [32.5, 389.0], [32.6, 389.0], [32.7, 389.0], [32.8, 389.0], [32.9, 389.0], [33.0, 389.0], [33.1, 389.0], [33.2, 390.0], [33.3, 390.0], [33.4, 390.0], [33.5, 390.0], [33.6, 390.0], [33.7, 390.0], [33.8, 390.0], [33.9, 390.0], [34.0, 390.0], [34.1, 390.0], [34.2, 390.0], [34.3, 390.0], [34.4, 390.0], [34.5, 391.0], [34.6, 391.0], [34.7, 391.0], [34.8, 391.0], [34.9, 391.0], [35.0, 391.0], [35.1, 391.0], [35.2, 391.0], [35.3, 391.0], [35.4, 391.0], [35.5, 391.0], [35.6, 391.0], [35.7, 391.0], [35.8, 391.0], [35.9, 391.0], [36.0, 391.0], [36.1, 392.0], [36.2, 392.0], [36.3, 392.0], [36.4, 392.0], [36.5, 392.0], [36.6, 392.0], [36.7, 392.0], [36.8, 392.0], [36.9, 392.0], [37.0, 392.0], [37.1, 393.0], [37.2, 393.0], [37.3, 393.0], [37.4, 393.0], [37.5, 393.0], [37.6, 393.0], [37.7, 393.0], [37.8, 393.0], [37.9, 393.0], [38.0, 393.0], [38.1, 393.0], [38.2, 394.0], [38.3, 394.0], [38.4, 394.0], [38.5, 394.0], [38.6, 394.0], [38.7, 394.0], [38.8, 394.0], [38.9, 394.0], [39.0, 394.0], [39.1, 395.0], [39.2, 395.0], [39.3, 395.0], [39.4, 395.0], [39.5, 395.0], [39.6, 395.0], [39.7, 395.0], [39.8, 395.0], [39.9, 395.0], [40.0, 395.0], [40.1, 395.0], [40.2, 395.0], [40.3, 396.0], [40.4, 396.0], [40.5, 396.0], [40.6, 396.0], [40.7, 396.0], [40.8, 396.0], [40.9, 396.0], [41.0, 396.0], [41.1, 396.0], [41.2, 397.0], [41.3, 397.0], [41.4, 397.0], [41.5, 397.0], [41.6, 397.0], [41.7, 397.0], [41.8, 397.0], [41.9, 397.0], [42.0, 397.0], [42.1, 397.0], [42.2, 397.0], [42.3, 397.0], [42.4, 397.0], [42.5, 398.0], [42.6, 398.0], [42.7, 398.0], [42.8, 398.0], [42.9, 398.0], [43.0, 398.0], [43.1, 398.0], [43.2, 398.0], [43.3, 398.0], [43.4, 398.0], [43.5, 398.0], [43.6, 398.0], [43.7, 398.0], [43.8, 399.0], [43.9, 399.0], [44.0, 399.0], [44.1, 399.0], [44.2, 399.0], [44.3, 399.0], [44.4, 400.0], [44.5, 400.0], [44.6, 400.0], [44.7, 400.0], [44.8, 400.0], [44.9, 400.0], [45.0, 400.0], [45.1, 400.0], [45.2, 400.0], [45.3, 401.0], [45.4, 401.0], [45.5, 401.0], [45.6, 401.0], [45.7, 401.0], [45.8, 401.0], [45.9, 401.0], [46.0, 401.0], [46.1, 401.0], [46.2, 401.0], [46.3, 401.0], [46.4, 401.0], [46.5, 401.0], [46.6, 401.0], [46.7, 402.0], [46.8, 402.0], [46.9, 402.0], [47.0, 402.0], [47.1, 402.0], [47.2, 402.0], [47.3, 402.0], [47.4, 402.0], [47.5, 402.0], [47.6, 402.0], [47.7, 402.0], [47.8, 402.0], [47.9, 402.0], [48.0, 402.0], [48.1, 402.0], [48.2, 403.0], [48.3, 403.0], [48.4, 403.0], [48.5, 403.0], [48.6, 403.0], [48.7, 403.0], [48.8, 403.0], [48.9, 403.0], [49.0, 403.0], [49.1, 403.0], [49.2, 403.0], [49.3, 403.0], [49.4, 403.0], [49.5, 403.0], [49.6, 404.0], [49.7, 404.0], [49.8, 404.0], [49.9, 404.0], [50.0, 404.0], [50.1, 404.0], [50.2, 404.0], [50.3, 404.0], [50.4, 404.0], [50.5, 404.0], [50.6, 404.0], [50.7, 404.0], [50.8, 405.0], [50.9, 405.0], [51.0, 405.0], [51.1, 405.0], [51.2, 405.0], [51.3, 405.0], [51.4, 405.0], [51.5, 405.0], [51.6, 406.0], [51.7, 406.0], [51.8, 406.0], [51.9, 406.0], [52.0, 406.0], [52.1, 406.0], [52.2, 406.0], [52.3, 406.0], [52.4, 406.0], [52.5, 407.0], [52.6, 407.0], [52.7, 407.0], [52.8, 407.0], [52.9, 407.0], [53.0, 407.0], [53.1, 407.0], [53.2, 407.0], [53.3, 407.0], [53.4, 407.0], [53.5, 407.0], [53.6, 408.0], [53.7, 408.0], [53.8, 408.0], [53.9, 408.0], [54.0, 408.0], [54.1, 408.0], [54.2, 408.0], [54.3, 408.0], [54.4, 408.0], [54.5, 408.0], [54.6, 408.0], [54.7, 408.0], [54.8, 408.0], [54.9, 409.0], [55.0, 409.0], [55.1, 409.0], [55.2, 409.0], [55.3, 409.0], [55.4, 409.0], [55.5, 409.0], [55.6, 409.0], [55.7, 409.0], [55.8, 410.0], [55.9, 410.0], [56.0, 410.0], [56.1, 410.0], [56.2, 410.0], [56.3, 410.0], [56.4, 410.0], [56.5, 410.0], [56.6, 410.0], [56.7, 410.0], [56.8, 410.0], [56.9, 411.0], [57.0, 411.0], [57.1, 411.0], [57.2, 411.0], [57.3, 411.0], [57.4, 411.0], [57.5, 411.0], [57.6, 411.0], [57.7, 411.0], [57.8, 411.0], [57.9, 411.0], [58.0, 412.0], [58.1, 412.0], [58.2, 412.0], [58.3, 412.0], [58.4, 412.0], [58.5, 412.0], [58.6, 412.0], [58.7, 412.0], [58.8, 412.0], [58.9, 412.0], [59.0, 413.0], [59.1, 413.0], [59.2, 413.0], [59.3, 413.0], [59.4, 413.0], [59.5, 414.0], [59.6, 414.0], [59.7, 414.0], [59.8, 414.0], [59.9, 414.0], [60.0, 414.0], [60.1, 414.0], [60.2, 415.0], [60.3, 415.0], [60.4, 415.0], [60.5, 415.0], [60.6, 415.0], [60.7, 415.0], [60.8, 415.0], [60.9, 415.0], [61.0, 415.0], [61.1, 416.0], [61.2, 416.0], [61.3, 416.0], [61.4, 416.0], [61.5, 416.0], [61.6, 416.0], [61.7, 417.0], [61.8, 417.0], [61.9, 417.0], [62.0, 417.0], [62.1, 417.0], [62.2, 417.0], [62.3, 417.0], [62.4, 418.0], [62.5, 418.0], [62.6, 418.0], [62.7, 418.0], [62.8, 418.0], [62.9, 418.0], [63.0, 418.0], [63.1, 418.0], [63.2, 418.0], [63.3, 419.0], [63.4, 419.0], [63.5, 419.0], [63.6, 419.0], [63.7, 419.0], [63.8, 419.0], [63.9, 419.0], [64.0, 420.0], [64.1, 420.0], [64.2, 420.0], [64.3, 420.0], [64.4, 420.0], [64.5, 421.0], [64.6, 421.0], [64.7, 421.0], [64.8, 421.0], [64.9, 422.0], [65.0, 422.0], [65.1, 422.0], [65.2, 423.0], [65.3, 423.0], [65.4, 423.0], [65.5, 423.0], [65.6, 423.0], [65.7, 423.0], [65.8, 424.0], [65.9, 424.0], [66.0, 424.0], [66.1, 424.0], [66.2, 425.0], [66.3, 425.0], [66.4, 425.0], [66.5, 426.0], [66.6, 426.0], [66.7, 426.0], [66.8, 426.0], [66.9, 427.0], [67.0, 427.0], [67.1, 428.0], [67.2, 428.0], [67.3, 428.0], [67.4, 428.0], [67.5, 429.0], [67.6, 429.0], [67.7, 430.0], [67.8, 430.0], [67.9, 431.0], [68.0, 431.0], [68.1, 431.0], [68.2, 432.0], [68.3, 432.0], [68.4, 432.0], [68.5, 433.0], [68.6, 433.0], [68.7, 433.0], [68.8, 435.0], [68.9, 436.0], [69.0, 436.0], [69.1, 437.0], [69.2, 437.0], [69.3, 438.0], [69.4, 438.0], [69.5, 439.0], [69.6, 439.0], [69.7, 440.0], [69.8, 441.0], [69.9, 441.0], [70.0, 442.0], [70.1, 443.0], [70.2, 443.0], [70.3, 444.0], [70.4, 444.0], [70.5, 444.0], [70.6, 444.0], [70.7, 445.0], [70.8, 445.0], [70.9, 446.0], [71.0, 446.0], [71.1, 447.0], [71.2, 447.0], [71.3, 448.0], [71.4, 448.0], [71.5, 449.0], [71.6, 449.0], [71.7, 450.0], [71.8, 450.0], [71.9, 451.0], [72.0, 452.0], [72.1, 452.0], [72.2, 453.0], [72.3, 454.0], [72.4, 454.0], [72.5, 455.0], [72.6, 455.0], [72.7, 455.0], [72.8, 456.0], [72.9, 458.0], [73.0, 458.0], [73.1, 458.0], [73.2, 460.0], [73.3, 461.0], [73.4, 463.0], [73.5, 464.0], [73.6, 465.0], [73.7, 465.0], [73.8, 467.0], [73.9, 468.0], [74.0, 470.0], [74.1, 471.0], [74.2, 472.0], [74.3, 472.0], [74.4, 474.0], [74.5, 477.0], [74.6, 477.0], [74.7, 478.0], [74.8, 479.0], [74.9, 480.0], [75.0, 481.0], [75.1, 481.0], [75.2, 482.0], [75.3, 482.0], [75.4, 482.0], [75.5, 483.0], [75.6, 483.0], [75.7, 484.0], [75.8, 485.0], [75.9, 486.0], [76.0, 487.0], [76.1, 488.0], [76.2, 488.0], [76.3, 488.0], [76.4, 488.0], [76.5, 489.0], [76.6, 489.0], [76.7, 489.0], [76.8, 489.0], [76.9, 491.0], [77.0, 491.0], [77.1, 492.0], [77.2, 493.0], [77.3, 493.0], [77.4, 494.0], [77.5, 494.0], [77.6, 494.0], [77.7, 495.0], [77.8, 496.0], [77.9, 497.0], [78.0, 497.0], [78.1, 497.0], [78.2, 498.0], [78.3, 499.0], [78.4, 500.0], [78.5, 501.0], [78.6, 501.0], [78.7, 501.0], [78.8, 502.0], [78.9, 502.0], [79.0, 502.0], [79.1, 503.0], [79.2, 504.0], [79.3, 504.0], [79.4, 504.0], [79.5, 505.0], [79.6, 506.0], [79.7, 506.0], [79.8, 506.0], [79.9, 506.0], [80.0, 507.0], [80.1, 507.0], [80.2, 508.0], [80.3, 508.0], [80.4, 508.0], [80.5, 508.0], [80.6, 509.0], [80.7, 510.0], [80.8, 510.0], [80.9, 510.0], [81.0, 510.0], [81.1, 511.0], [81.2, 511.0], [81.3, 512.0], [81.4, 512.0], [81.5, 513.0], [81.6, 513.0], [81.7, 514.0], [81.8, 514.0], [81.9, 515.0], [82.0, 515.0], [82.1, 515.0], [82.2, 516.0], [82.3, 516.0], [82.4, 517.0], [82.5, 517.0], [82.6, 518.0], [82.7, 518.0], [82.8, 518.0], [82.9, 518.0], [83.0, 518.0], [83.1, 519.0], [83.2, 519.0], [83.3, 519.0], [83.4, 520.0], [83.5, 520.0], [83.6, 521.0], [83.7, 521.0], [83.8, 521.0], [83.9, 521.0], [84.0, 522.0], [84.1, 522.0], [84.2, 522.0], [84.3, 523.0], [84.4, 523.0], [84.5, 524.0], [84.6, 524.0], [84.7, 524.0], [84.8, 524.0], [84.9, 525.0], [85.0, 525.0], [85.1, 525.0], [85.2, 526.0], [85.3, 526.0], [85.4, 526.0], [85.5, 527.0], [85.6, 527.0], [85.7, 528.0], [85.8, 528.0], [85.9, 528.0], [86.0, 529.0], [86.1, 529.0], [86.2, 529.0], [86.3, 529.0], [86.4, 530.0], [86.5, 530.0], [86.6, 531.0], [86.7, 531.0], [86.8, 531.0], [86.9, 531.0], [87.0, 532.0], [87.1, 532.0], [87.2, 532.0], [87.3, 533.0], [87.4, 533.0], [87.5, 534.0], [87.6, 534.0], [87.7, 534.0], [87.8, 535.0], [87.9, 535.0], [88.0, 535.0], [88.1, 535.0], [88.2, 536.0], [88.3, 536.0], [88.4, 537.0], [88.5, 537.0], [88.6, 538.0], [88.7, 538.0], [88.8, 539.0], [88.9, 539.0], [89.0, 540.0], [89.1, 540.0], [89.2, 541.0], [89.3, 541.0], [89.4, 542.0], [89.5, 542.0], [89.6, 542.0], [89.7, 543.0], [89.8, 543.0], [89.9, 543.0], [90.0, 544.0], [90.1, 544.0], [90.2, 544.0], [90.3, 544.0], [90.4, 544.0], [90.5, 544.0], [90.6, 545.0], [90.7, 545.0], [90.8, 545.0], [90.9, 546.0], [91.0, 546.0], [91.1, 546.0], [91.2, 547.0], [91.3, 547.0], [91.4, 547.0], [91.5, 548.0], [91.6, 548.0], [91.7, 549.0], [91.8, 549.0], [91.9, 550.0], [92.0, 550.0], [92.1, 550.0], [92.2, 551.0], [92.3, 551.0], [92.4, 551.0], [92.5, 551.0], [92.6, 551.0], [92.7, 552.0], [92.8, 552.0], [92.9, 552.0], [93.0, 553.0], [93.1, 553.0], [93.2, 553.0], [93.3, 553.0], [93.4, 554.0], [93.5, 554.0], [93.6, 554.0], [93.7, 555.0], [93.8, 556.0], [93.9, 556.0], [94.0, 557.0], [94.1, 557.0], [94.2, 557.0], [94.3, 557.0], [94.4, 557.0], [94.5, 558.0], [94.6, 558.0], [94.7, 558.0], [94.8, 559.0], [94.9, 559.0], [95.0, 560.0], [95.1, 560.0], [95.2, 561.0], [95.3, 562.0], [95.4, 562.0], [95.5, 562.0], [95.6, 562.0], [95.7, 563.0], [95.8, 564.0], [95.9, 564.0], [96.0, 564.0], [96.1, 565.0], [96.2, 566.0], [96.3, 567.0], [96.4, 567.0], [96.5, 567.0], [96.6, 568.0], [96.7, 569.0], [96.8, 569.0], [96.9, 570.0], [97.0, 571.0], [97.1, 572.0], [97.2, 572.0], [97.3, 573.0], [97.4, 573.0], [97.5, 576.0], [97.6, 576.0], [97.7, 577.0], [97.8, 578.0], [97.9, 578.0], [98.0, 580.0], [98.1, 581.0], [98.2, 585.0], [98.3, 586.0], [98.4, 588.0], [98.5, 593.0], [98.6, 597.0], [98.7, 604.0], [98.8, 626.0], [98.9, 658.0], [99.0, 668.0], [99.1, 679.0], [99.2, 694.0], [99.3, 697.0], [99.4, 702.0], [99.5, 715.0], [99.6, 720.0], [99.7, 726.0], [99.8, 737.0], [99.9, 751.0]], "isOverall": false, "label": "HTTP请求", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 100.0, "title": "Response Time Percentiles"}},
        getOptions: function() {
            return {
                series: {
                    points: { show: false }
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendResponseTimePercentiles'
                },
                xaxis: {
                    tickDecimals: 1,
                    axisLabel: "Percentiles",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Percentile value in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : %x.2 percentile was %y ms"
                },
                selection: { mode: "xy" },
            };
        },
        createGraph: function() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesResponseTimePercentiles"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotResponseTimesPercentiles"), dataset, options);
            // setup overview
            $.plot($("#overviewResponseTimesPercentiles"), dataset, prepareOverviewOptions(options));
        }
};

/**
 * @param elementId Id of element where we display message
 */
function setEmptyGraph(elementId) {
    $(function() {
        $(elementId).text("No graph series with filter="+seriesFilter);
    });
}

// Response times percentiles
function refreshResponseTimePercentiles() {
    var infos = responseTimePercentilesInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyResponseTimePercentiles");
        return;
    }
    if (isGraph($("#flotResponseTimesPercentiles"))){
        infos.createGraph();
    } else {
        var choiceContainer = $("#choicesResponseTimePercentiles");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotResponseTimesPercentiles", "#overviewResponseTimesPercentiles");
        $('#bodyResponseTimePercentiles .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
}

var responseTimeDistributionInfos = {
        data: {"result": {"minY": 13.0, "minX": 0.0, "maxY": 754.0, "series": [{"data": [[0.0, 18.0], [300.0, 754.0], [600.0, 13.0], [700.0, 13.0], [100.0, 21.0], [200.0, 94.0], [400.0, 681.0], [500.0, 406.0]], "isOverall": false, "label": "HTTP请求", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 100, "maxX": 700.0, "title": "Response Time Distribution"}},
        getOptions: function() {
            var granularity = this.data.result.granularity;
            return {
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendResponseTimeDistribution'
                },
                xaxis:{
                    axisLabel: "Response times in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of responses",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                bars : {
                    show: true,
                    barWidth: this.data.result.granularity
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: function(label, xval, yval, flotItem){
                        return yval + " responses for " + label + " were between " + xval + " and " + (xval + granularity) + " ms";
                    }
                }
            };
        },
        createGraph: function() {
            var data = this.data;
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotResponseTimeDistribution"), prepareData(data.result.series, $("#choicesResponseTimeDistribution")), options);
        }

};

// Response time distribution
function refreshResponseTimeDistribution() {
    var infos = responseTimeDistributionInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyResponseTimeDistribution");
        return;
    }
    if (isGraph($("#flotResponseTimeDistribution"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesResponseTimeDistribution");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        $('#footerResponseTimeDistribution .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};


var syntheticResponseTimeDistributionInfos = {
        data: {"result": {"minY": 430.0, "minX": 0.0, "ticks": [[0, "Requests having \nresponse time <= 500ms"], [1, "Requests having \nresponse time > 500ms and <= 1,500ms"], [2, "Requests having \nresponse time > 1,500ms"], [3, "Requests in error"]], "maxY": 1570.0, "series": [{"data": [[0.0, 1570.0]], "color": "#9ACD32", "isOverall": false, "label": "Requests having \nresponse time <= 500ms", "isController": false}, {"data": [[1.0, 430.0]], "color": "yellow", "isOverall": false, "label": "Requests having \nresponse time > 500ms and <= 1,500ms", "isController": false}, {"data": [], "color": "orange", "isOverall": false, "label": "Requests having \nresponse time > 1,500ms", "isController": false}, {"data": [], "color": "#FF6347", "isOverall": false, "label": "Requests in error", "isController": false}], "supportsControllersDiscrimination": false, "maxX": 1.0, "title": "Synthetic Response Times Distribution"}},
        getOptions: function() {
            return {
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendSyntheticResponseTimeDistribution'
                },
                xaxis:{
                    axisLabel: "Response times ranges",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                    tickLength:0,
                    min:-0.5,
                    max:3.5
                },
                yaxis: {
                    axisLabel: "Number of responses",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                bars : {
                    show: true,
                    align: "center",
                    barWidth: 0.25,
                    fill:.75
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: function(label, xval, yval, flotItem){
                        return yval + " " + label;
                    }
                }
            };
        },
        createGraph: function() {
            var data = this.data;
            var options = this.getOptions();
            prepareOptions(options, data);
            options.xaxis.ticks = data.result.ticks;
            $.plot($("#flotSyntheticResponseTimeDistribution"), prepareData(data.result.series, $("#choicesSyntheticResponseTimeDistribution")), options);
        }

};

// Response time distribution
function refreshSyntheticResponseTimeDistribution() {
    var infos = syntheticResponseTimeDistributionInfos;
    prepareSeries(infos.data, true);
    if (isGraph($("#flotSyntheticResponseTimeDistribution"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesSyntheticResponseTimeDistribution");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        $('#footerSyntheticResponseTimeDistribution .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var activeThreadsOverTimeInfos = {
        data: {"result": {"minY": 19.55235042735043, "minX": 1.79315622E12, "maxY": 19.788533834586445, "series": [{"data": [[1.79315628E12, 19.55235042735043], [1.79315622E12, 19.788533834586445]], "isOverall": false, "label": "线程组", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79315628E12, "title": "Active Threads Over Time"}},
        getOptions: function() {
            return {
                series: {
                    stack: true,
                    lines: {
                        show: true,
                        fill: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of active threads",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                legend: {
                    noColumns: 6,
                    show: true,
                    container: '#legendActiveThreadsOverTime'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                selection: {
                    mode: 'xy'
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : At %x there were %y active threads"
                }
            };
        },
        createGraph: function() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesActiveThreadsOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotActiveThreadsOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewActiveThreadsOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Active Threads Over Time
function refreshActiveThreadsOverTime(fixTimestamps) {
    var infos = activeThreadsOverTimeInfos;
    prepareSeries(infos.data);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 28800000);
    }
    if(isGraph($("#flotActiveThreadsOverTime"))) {
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesActiveThreadsOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotActiveThreadsOverTime", "#overviewActiveThreadsOverTime");
        $('#footerActiveThreadsOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var timeVsThreadsInfos = {
        data: {"result": {"minY": 33.0, "minX": 1.0, "maxY": 427.47528916929474, "series": [{"data": [[8.0, 118.4], [2.0, 57.0], [9.0, 183.66666666666666], [10.0, 151.5], [11.0, 174.2], [3.0, 52.0], [12.0, 205.8], [13.0, 219.0], [14.0, 272.6], [15.0, 333.4], [4.0, 38.5], [16.0, 327.4545454545455], [1.0, 35.0], [17.0, 229.4], [18.0, 424.0], [19.0, 404.0], [5.0, 33.0], [20.0, 427.47528916929474], [6.0, 75.0], [7.0, 82.0]], "isOverall": false, "label": "HTTP请求", "isController": false}, {"data": [[19.677999999999958, 419.5029999999999]], "isOverall": false, "label": "HTTP请求-Aggregated", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 20.0, "title": "Time VS Threads"}},
        getOptions: function() {
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    axisLabel: "Number of active threads",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Average response times in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                legend: { noColumns: 2,show: true, container: '#legendTimeVsThreads' },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s: At %x.2 active threads, Average response time was %y.2 ms"
                }
            };
        },
        createGraph: function() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesTimeVsThreads"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotTimesVsThreads"), dataset, options);
            // setup overview
            $.plot($("#overviewTimesVsThreads"), dataset, prepareOverviewOptions(options));
        }
};

// Time vs threads
function refreshTimeVsThreads(){
    var infos = timeVsThreadsInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyTimeVsThreads");
        return;
    }
    if(isGraph($("#flotTimesVsThreads"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesTimeVsThreads");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotTimesVsThreads", "#overviewTimesVsThreads");
        $('#footerTimeVsThreads .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var bytesThroughputOverTimeInfos = {
        data : {"result": {"minY": 8314.8, "minX": 1.79315622E12, "maxY": 34562.26666666667, "series": [{"data": [[1.79315628E12, 30404.4], [1.79315622E12, 34562.26666666667]], "isOverall": false, "label": "Bytes received per second", "isController": false}, {"data": [[1.79315628E12, 8314.8], [1.79315622E12, 9451.866666666667]], "isOverall": false, "label": "Bytes sent per second", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79315628E12, "title": "Bytes Throughput Over Time"}},
        getOptions : function(){
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity) ,
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Bytes / sec",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendBytesThroughputOverTime'
                },
                selection: {
                    mode: "xy"
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s at %x was %y"
                }
            };
        },
        createGraph : function() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesBytesThroughputOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotBytesThroughputOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewBytesThroughputOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Bytes throughput Over Time
function refreshBytesThroughputOverTime(fixTimestamps) {
    var infos = bytesThroughputOverTimeInfos;
    prepareSeries(infos.data);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 28800000);
    }
    if(isGraph($("#flotBytesThroughputOverTime"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesBytesThroughputOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotBytesThroughputOverTime", "#overviewBytesThroughputOverTime");
        $('#footerBytesThroughputOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
}

var responseTimesOverTimeInfos = {
        data: {"result": {"minY": 403.3251879699246, "minX": 1.79315622E12, "maxY": 437.89316239316224, "series": [{"data": [[1.79315628E12, 437.89316239316224], [1.79315622E12, 403.3251879699246]], "isOverall": false, "label": "HTTP请求", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79315628E12, "title": "Response Time Over Time"}},
        getOptions: function(){
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Average response time in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendResponseTimesOverTime'
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : at %x Average response time was %y ms"
                }
            };
        },
        createGraph: function() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesResponseTimesOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotResponseTimesOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewResponseTimesOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Response Times Over Time
function refreshResponseTimeOverTime(fixTimestamps) {
    var infos = responseTimesOverTimeInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyResponseTimeOverTime");
        return;
    }
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 28800000);
    }
    if(isGraph($("#flotResponseTimesOverTime"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesResponseTimesOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotResponseTimesOverTime", "#overviewResponseTimesOverTime");
        $('#footerResponseTimesOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var latenciesOverTimeInfos = {
        data: {"result": {"minY": 403.22744360902254, "minX": 1.79315622E12, "maxY": 437.77991452991466, "series": [{"data": [[1.79315628E12, 437.77991452991466], [1.79315622E12, 403.22744360902254]], "isOverall": false, "label": "HTTP请求", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79315628E12, "title": "Latencies Over Time"}},
        getOptions: function() {
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Average response latencies in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendLatenciesOverTime'
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : at %x Average latency was %y ms"
                }
            };
        },
        createGraph: function () {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesLatenciesOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotLatenciesOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewLatenciesOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Latencies Over Time
function refreshLatenciesOverTime(fixTimestamps) {
    var infos = latenciesOverTimeInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyLatenciesOverTime");
        return;
    }
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 28800000);
    }
    if(isGraph($("#flotLatenciesOverTime"))) {
        infos.createGraph();
    }else {
        var choiceContainer = $("#choicesLatenciesOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotLatenciesOverTime", "#overviewLatenciesOverTime");
        $('#footerLatenciesOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var connectTimeOverTimeInfos = {
        data: {"result": {"minY": 0.8186090225563912, "minX": 1.79315622E12, "maxY": 0.9455128205128207, "series": [{"data": [[1.79315628E12, 0.9455128205128207], [1.79315622E12, 0.8186090225563912]], "isOverall": false, "label": "HTTP请求", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79315628E12, "title": "Connect Time Over Time"}},
        getOptions: function() {
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getConnectTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Average Connect Time in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendConnectTimeOverTime'
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : at %x Average connect time was %y ms"
                }
            };
        },
        createGraph: function () {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesConnectTimeOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotConnectTimeOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewConnectTimeOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Connect Time Over Time
function refreshConnectTimeOverTime(fixTimestamps) {
    var infos = connectTimeOverTimeInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyConnectTimeOverTime");
        return;
    }
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 28800000);
    }
    if(isGraph($("#flotConnectTimeOverTime"))) {
        infos.createGraph();
    }else {
        var choiceContainer = $("#choicesConnectTimeOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotConnectTimeOverTime", "#overviewConnectTimeOverTime");
        $('#footerConnectTimeOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var responseTimePercentilesOverTimeInfos = {
        data: {"result": {"minY": 20.0, "minX": 1.79315622E12, "maxY": 755.0, "series": [{"data": [[1.79315628E12, 726.0], [1.79315622E12, 755.0]], "isOverall": false, "label": "Max", "isController": false}, {"data": [[1.79315628E12, 35.0], [1.79315622E12, 20.0]], "isOverall": false, "label": "Min", "isController": false}, {"data": [[1.79315628E12, 546.0], [1.79315622E12, 537.5]], "isOverall": false, "label": "90th percentile", "isController": false}, {"data": [[1.79315628E12, 654.3], [1.79315622E12, 673.1499999999992]], "isOverall": false, "label": "99th percentile", "isController": false}, {"data": [[1.79315628E12, 412.0], [1.79315622E12, 394.0]], "isOverall": false, "label": "Median", "isController": false}, {"data": [[1.79315628E12, 561.15], [1.79315622E12, 558.75]], "isOverall": false, "label": "95th percentile", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79315628E12, "title": "Response Time Percentiles Over Time (successful requests only)"}},
        getOptions: function() {
            return {
                series: {
                    lines: {
                        show: true,
                        fill: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Response Time in ms",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: '#legendResponseTimePercentilesOverTime'
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s : at %x Response time was %y ms"
                }
            };
        },
        createGraph: function () {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesResponseTimePercentilesOverTime"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotResponseTimePercentilesOverTime"), dataset, options);
            // setup overview
            $.plot($("#overviewResponseTimePercentilesOverTime"), dataset, prepareOverviewOptions(options));
        }
};

// Response Time Percentiles Over Time
function refreshResponseTimePercentilesOverTime(fixTimestamps) {
    var infos = responseTimePercentilesOverTimeInfos;
    prepareSeries(infos.data);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 28800000);
    }
    if(isGraph($("#flotResponseTimePercentilesOverTime"))) {
        infos.createGraph();
    }else {
        var choiceContainer = $("#choicesResponseTimePercentilesOverTime");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotResponseTimePercentilesOverTime", "#overviewResponseTimePercentilesOverTime");
        $('#footerResponseTimePercentilesOverTime .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};


var responseTimeVsRequestInfos = {
    data: {"result": {"minY": 119.5, "minX": 26.0, "maxY": 414.5, "series": [{"data": [[33.0, 410.0], [34.0, 407.5], [35.0, 414.5], [37.0, 407.5], [36.0, 410.5], [38.0, 414.0], [39.0, 400.0], [41.0, 389.0], [40.0, 397.0], [42.0, 357.0], [50.0, 298.0], [54.0, 321.5], [26.0, 119.5]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 54.0, "title": "Response Time Vs Request"}},
    getOptions: function() {
        return {
            series: {
                lines: {
                    show: false
                },
                points: {
                    show: true
                }
            },
            xaxis: {
                axisLabel: "Global number of requests per second",
                axisLabelUseCanvas: true,
                axisLabelFontSizePixels: 12,
                axisLabelFontFamily: 'Verdana, Arial',
                axisLabelPadding: 20,
            },
            yaxis: {
                axisLabel: "Median Response Time in ms",
                axisLabelUseCanvas: true,
                axisLabelFontSizePixels: 12,
                axisLabelFontFamily: 'Verdana, Arial',
                axisLabelPadding: 20,
            },
            legend: {
                noColumns: 2,
                show: true,
                container: '#legendResponseTimeVsRequest'
            },
            selection: {
                mode: 'xy'
            },
            grid: {
                hoverable: true // IMPORTANT! this is needed for tooltip to work
            },
            tooltip: true,
            tooltipOpts: {
                content: "%s : Median response time at %x req/s was %y ms"
            },
            colors: ["#9ACD32", "#FF6347"]
        };
    },
    createGraph: function () {
        var data = this.data;
        var dataset = prepareData(data.result.series, $("#choicesResponseTimeVsRequest"));
        var options = this.getOptions();
        prepareOptions(options, data);
        $.plot($("#flotResponseTimeVsRequest"), dataset, options);
        // setup overview
        $.plot($("#overviewResponseTimeVsRequest"), dataset, prepareOverviewOptions(options));

    }
};

// Response Time vs Request
function refreshResponseTimeVsRequest() {
    var infos = responseTimeVsRequestInfos;
    prepareSeries(infos.data);
    if (isGraph($("#flotResponseTimeVsRequest"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesResponseTimeVsRequest");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotResponseTimeVsRequest", "#overviewResponseTimeVsRequest");
        $('#footerResponseRimeVsRequest .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};


var latenciesVsRequestInfos = {
    data: {"result": {"minY": 119.5, "minX": 26.0, "maxY": 414.0, "series": [{"data": [[33.0, 410.0], [34.0, 407.5], [35.0, 414.0], [37.0, 407.5], [36.0, 410.5], [38.0, 414.0], [39.0, 400.0], [41.0, 389.0], [40.0, 397.0], [42.0, 357.0], [50.0, 298.0], [54.0, 321.0], [26.0, 119.5]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 54.0, "title": "Latencies Vs Request"}},
    getOptions: function() {
        return{
            series: {
                lines: {
                    show: false
                },
                points: {
                    show: true
                }
            },
            xaxis: {
                axisLabel: "Global number of requests per second",
                axisLabelUseCanvas: true,
                axisLabelFontSizePixels: 12,
                axisLabelFontFamily: 'Verdana, Arial',
                axisLabelPadding: 20,
            },
            yaxis: {
                axisLabel: "Median Latency in ms",
                axisLabelUseCanvas: true,
                axisLabelFontSizePixels: 12,
                axisLabelFontFamily: 'Verdana, Arial',
                axisLabelPadding: 20,
            },
            legend: { noColumns: 2,show: true, container: '#legendLatencyVsRequest' },
            selection: {
                mode: 'xy'
            },
            grid: {
                hoverable: true // IMPORTANT! this is needed for tooltip to work
            },
            tooltip: true,
            tooltipOpts: {
                content: "%s : Median Latency time at %x req/s was %y ms"
            },
            colors: ["#9ACD32", "#FF6347"]
        };
    },
    createGraph: function () {
        var data = this.data;
        var dataset = prepareData(data.result.series, $("#choicesLatencyVsRequest"));
        var options = this.getOptions();
        prepareOptions(options, data);
        $.plot($("#flotLatenciesVsRequest"), dataset, options);
        // setup overview
        $.plot($("#overviewLatenciesVsRequest"), dataset, prepareOverviewOptions(options));
    }
};

// Latencies vs Request
function refreshLatenciesVsRequest() {
        var infos = latenciesVsRequestInfos;
        prepareSeries(infos.data);
        if(isGraph($("#flotLatenciesVsRequest"))){
            infos.createGraph();
        }else{
            var choiceContainer = $("#choicesLatencyVsRequest");
            createLegend(choiceContainer, infos);
            infos.createGraph();
            setGraphZoomable("#flotLatenciesVsRequest", "#overviewLatenciesVsRequest");
            $('#footerLatenciesVsRequest .legendColorBox > div').each(function(i){
                $(this).clone().prependTo(choiceContainer.find("li").eq(i));
            });
        }
};

var hitsPerSecondInfos = {
        data: {"result": {"minY": 15.366666666666667, "minX": 1.79315622E12, "maxY": 17.966666666666665, "series": [{"data": [[1.79315628E12, 15.366666666666667], [1.79315622E12, 17.966666666666665]], "isOverall": false, "label": "hitsPerSecond", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79315628E12, "title": "Hits Per Second"}},
        getOptions: function() {
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of hits / sec",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: "#legendHitsPerSecond"
                },
                selection: {
                    mode : 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s at %x was %y.2 hits/sec"
                }
            };
        },
        createGraph: function createGraph() {
            var data = this.data;
            var dataset = prepareData(data.result.series, $("#choicesHitsPerSecond"));
            var options = this.getOptions();
            prepareOptions(options, data);
            $.plot($("#flotHitsPerSecond"), dataset, options);
            // setup overview
            $.plot($("#overviewHitsPerSecond"), dataset, prepareOverviewOptions(options));
        }
};

// Hits per second
function refreshHitsPerSecond(fixTimestamps) {
    var infos = hitsPerSecondInfos;
    prepareSeries(infos.data);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 28800000);
    }
    if (isGraph($("#flotHitsPerSecond"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesHitsPerSecond");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotHitsPerSecond", "#overviewHitsPerSecond");
        $('#footerHitsPerSecond .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
}

var codesPerSecondInfos = {
        data: {"result": {"minY": 15.6, "minX": 1.79315622E12, "maxY": 17.733333333333334, "series": [{"data": [[1.79315628E12, 15.6], [1.79315622E12, 17.733333333333334]], "isOverall": false, "label": "200", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79315628E12, "title": "Codes Per Second"}},
        getOptions: function(){
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of responses / sec",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: "#legendCodesPerSecond"
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "Number of Response Codes %s at %x was %y.2 responses / sec"
                }
            };
        },
    createGraph: function() {
        var data = this.data;
        var dataset = prepareData(data.result.series, $("#choicesCodesPerSecond"));
        var options = this.getOptions();
        prepareOptions(options, data);
        $.plot($("#flotCodesPerSecond"), dataset, options);
        // setup overview
        $.plot($("#overviewCodesPerSecond"), dataset, prepareOverviewOptions(options));
    }
};

// Codes per second
function refreshCodesPerSecond(fixTimestamps) {
    var infos = codesPerSecondInfos;
    prepareSeries(infos.data);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 28800000);
    }
    if(isGraph($("#flotCodesPerSecond"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesCodesPerSecond");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotCodesPerSecond", "#overviewCodesPerSecond");
        $('#footerCodesPerSecond .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var transactionsPerSecondInfos = {
        data: {"result": {"minY": 15.6, "minX": 1.79315622E12, "maxY": 17.733333333333334, "series": [{"data": [[1.79315628E12, 15.6], [1.79315622E12, 17.733333333333334]], "isOverall": false, "label": "HTTP请求-success", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79315628E12, "title": "Transactions Per Second"}},
        getOptions: function(){
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of transactions / sec",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: "#legendTransactionsPerSecond"
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s at %x was %y transactions / sec"
                }
            };
        },
    createGraph: function () {
        var data = this.data;
        var dataset = prepareData(data.result.series, $("#choicesTransactionsPerSecond"));
        var options = this.getOptions();
        prepareOptions(options, data);
        $.plot($("#flotTransactionsPerSecond"), dataset, options);
        // setup overview
        $.plot($("#overviewTransactionsPerSecond"), dataset, prepareOverviewOptions(options));
    }
};

// Transactions per second
function refreshTransactionsPerSecond(fixTimestamps) {
    var infos = transactionsPerSecondInfos;
    prepareSeries(infos.data);
    if(infos.data.result.series.length == 0) {
        setEmptyGraph("#bodyTransactionsPerSecond");
        return;
    }
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 28800000);
    }
    if(isGraph($("#flotTransactionsPerSecond"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesTransactionsPerSecond");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotTransactionsPerSecond", "#overviewTransactionsPerSecond");
        $('#footerTransactionsPerSecond .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

var totalTPSInfos = {
        data: {"result": {"minY": 15.6, "minX": 1.79315622E12, "maxY": 17.733333333333334, "series": [{"data": [[1.79315628E12, 15.6], [1.79315622E12, 17.733333333333334]], "isOverall": false, "label": "Transaction-success", "isController": false}, {"data": [], "isOverall": false, "label": "Transaction-failure", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79315628E12, "title": "Total Transactions Per Second"}},
        getOptions: function(){
            return {
                series: {
                    lines: {
                        show: true
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    mode: "time",
                    timeformat: getTimeFormat(this.data.result.granularity),
                    axisLabel: getElapsedTimeLabel(this.data.result.granularity),
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20,
                },
                yaxis: {
                    axisLabel: "Number of transactions / sec",
                    axisLabelUseCanvas: true,
                    axisLabelFontSizePixels: 12,
                    axisLabelFontFamily: 'Verdana, Arial',
                    axisLabelPadding: 20
                },
                legend: {
                    noColumns: 2,
                    show: true,
                    container: "#legendTotalTPS"
                },
                selection: {
                    mode: 'xy'
                },
                grid: {
                    hoverable: true // IMPORTANT! this is needed for tooltip to
                                    // work
                },
                tooltip: true,
                tooltipOpts: {
                    content: "%s at %x was %y transactions / sec"
                },
                colors: ["#9ACD32", "#FF6347"]
            };
        },
    createGraph: function () {
        var data = this.data;
        var dataset = prepareData(data.result.series, $("#choicesTotalTPS"));
        var options = this.getOptions();
        prepareOptions(options, data);
        $.plot($("#flotTotalTPS"), dataset, options);
        // setup overview
        $.plot($("#overviewTotalTPS"), dataset, prepareOverviewOptions(options));
    }
};

// Total Transactions per second
function refreshTotalTPS(fixTimestamps) {
    var infos = totalTPSInfos;
    // We want to ignore seriesFilter
    prepareSeries(infos.data, false, true);
    if(fixTimestamps) {
        fixTimeStamps(infos.data.result.series, 28800000);
    }
    if(isGraph($("#flotTotalTPS"))){
        infos.createGraph();
    }else{
        var choiceContainer = $("#choicesTotalTPS");
        createLegend(choiceContainer, infos);
        infos.createGraph();
        setGraphZoomable("#flotTotalTPS", "#overviewTotalTPS");
        $('#footerTotalTPS .legendColorBox > div').each(function(i){
            $(this).clone().prependTo(choiceContainer.find("li").eq(i));
        });
    }
};

// Collapse the graph matching the specified DOM element depending the collapsed
// status
function collapse(elem, collapsed){
    if(collapsed){
        $(elem).parent().find(".fa-chevron-up").removeClass("fa-chevron-up").addClass("fa-chevron-down");
    } else {
        $(elem).parent().find(".fa-chevron-down").removeClass("fa-chevron-down").addClass("fa-chevron-up");
        if (elem.id == "bodyBytesThroughputOverTime") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshBytesThroughputOverTime(true);
            }
            document.location.href="#bytesThroughputOverTime";
        } else if (elem.id == "bodyLatenciesOverTime") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshLatenciesOverTime(true);
            }
            document.location.href="#latenciesOverTime";
        } else if (elem.id == "bodyCustomGraph") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshCustomGraph(true);
            }
            document.location.href="#responseCustomGraph";
        } else if (elem.id == "bodyConnectTimeOverTime") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshConnectTimeOverTime(true);
            }
            document.location.href="#connectTimeOverTime";
        } else if (elem.id == "bodyResponseTimePercentilesOverTime") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshResponseTimePercentilesOverTime(true);
            }
            document.location.href="#responseTimePercentilesOverTime";
        } else if (elem.id == "bodyResponseTimeDistribution") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshResponseTimeDistribution();
            }
            document.location.href="#responseTimeDistribution" ;
        } else if (elem.id == "bodySyntheticResponseTimeDistribution") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshSyntheticResponseTimeDistribution();
            }
            document.location.href="#syntheticResponseTimeDistribution" ;
        } else if (elem.id == "bodyActiveThreadsOverTime") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshActiveThreadsOverTime(true);
            }
            document.location.href="#activeThreadsOverTime";
        } else if (elem.id == "bodyTimeVsThreads") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshTimeVsThreads();
            }
            document.location.href="#timeVsThreads" ;
        } else if (elem.id == "bodyCodesPerSecond") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshCodesPerSecond(true);
            }
            document.location.href="#codesPerSecond";
        } else if (elem.id == "bodyTransactionsPerSecond") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshTransactionsPerSecond(true);
            }
            document.location.href="#transactionsPerSecond";
        } else if (elem.id == "bodyTotalTPS") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshTotalTPS(true);
            }
            document.location.href="#totalTPS";
        } else if (elem.id == "bodyResponseTimeVsRequest") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshResponseTimeVsRequest();
            }
            document.location.href="#responseTimeVsRequest";
        } else if (elem.id == "bodyLatenciesVsRequest") {
            if (isGraph($(elem).find('.flot-chart-content')) == false) {
                refreshLatenciesVsRequest();
            }
            document.location.href="#latencyVsRequest";
        }
    }
}

/*
 * Activates or deactivates all series of the specified graph (represented by id parameter)
 * depending on checked argument.
 */
function toggleAll(id, checked){
    var placeholder = document.getElementById(id);

    var cases = $(placeholder).find(':checkbox');
    cases.prop('checked', checked);
    $(cases).parent().children().children().toggleClass("legend-disabled", !checked);

    var choiceContainer;
    if ( id == "choicesBytesThroughputOverTime"){
        choiceContainer = $("#choicesBytesThroughputOverTime");
        refreshBytesThroughputOverTime(false);
    } else if(id == "choicesResponseTimesOverTime"){
        choiceContainer = $("#choicesResponseTimesOverTime");
        refreshResponseTimeOverTime(false);
    }else if(id == "choicesResponseCustomGraph"){
        choiceContainer = $("#choicesResponseCustomGraph");
        refreshCustomGraph(false);
    } else if ( id == "choicesLatenciesOverTime"){
        choiceContainer = $("#choicesLatenciesOverTime");
        refreshLatenciesOverTime(false);
    } else if ( id == "choicesConnectTimeOverTime"){
        choiceContainer = $("#choicesConnectTimeOverTime");
        refreshConnectTimeOverTime(false);
    } else if ( id == "choicesResponseTimePercentilesOverTime"){
        choiceContainer = $("#choicesResponseTimePercentilesOverTime");
        refreshResponseTimePercentilesOverTime(false);
    } else if ( id == "choicesResponseTimePercentiles"){
        choiceContainer = $("#choicesResponseTimePercentiles");
        refreshResponseTimePercentiles();
    } else if(id == "choicesActiveThreadsOverTime"){
        choiceContainer = $("#choicesActiveThreadsOverTime");
        refreshActiveThreadsOverTime(false);
    } else if ( id == "choicesTimeVsThreads"){
        choiceContainer = $("#choicesTimeVsThreads");
        refreshTimeVsThreads();
    } else if ( id == "choicesSyntheticResponseTimeDistribution"){
        choiceContainer = $("#choicesSyntheticResponseTimeDistribution");
        refreshSyntheticResponseTimeDistribution();
    } else if ( id == "choicesResponseTimeDistribution"){
        choiceContainer = $("#choicesResponseTimeDistribution");
        refreshResponseTimeDistribution();
    } else if ( id == "choicesHitsPerSecond"){
        choiceContainer = $("#choicesHitsPerSecond");
        refreshHitsPerSecond(false);
    } else if(id == "choicesCodesPerSecond"){
        choiceContainer = $("#choicesCodesPerSecond");
        refreshCodesPerSecond(false);
    } else if ( id == "choicesTransactionsPerSecond"){
        choiceContainer = $("#choicesTransactionsPerSecond");
        refreshTransactionsPerSecond(false);
    } else if ( id == "choicesTotalTPS"){
        choiceContainer = $("#choicesTotalTPS");
        refreshTotalTPS(false);
    } else if ( id == "choicesResponseTimeVsRequest"){
        choiceContainer = $("#choicesResponseTimeVsRequest");
        refreshResponseTimeVsRequest();
    } else if ( id == "choicesLatencyVsRequest"){
        choiceContainer = $("#choicesLatencyVsRequest");
        refreshLatenciesVsRequest();
    }
    var color = checked ? "black" : "#818181";
    if(choiceContainer != null) {
        choiceContainer.find("label").each(function(){
            this.style.color = color;
        });
    }
}

