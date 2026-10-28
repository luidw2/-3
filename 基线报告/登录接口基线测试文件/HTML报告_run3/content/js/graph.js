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
        data: {"result": {"minY": 244.0, "minX": 0.0, "maxY": 1147.0, "series": [{"data": [[0.0, 244.0], [0.1, 245.0], [0.2, 249.0], [0.3, 250.0], [0.4, 253.0], [0.5, 258.0], [0.6, 261.0], [0.7, 263.0], [0.8, 268.0], [0.9, 270.0], [1.0, 272.0], [1.1, 273.0], [1.2, 276.0], [1.3, 276.0], [1.4, 277.0], [1.5, 281.0], [1.6, 282.0], [1.7, 286.0], [1.8, 287.0], [1.9, 288.0], [2.0, 290.0], [2.1, 291.0], [2.2, 292.0], [2.3, 295.0], [2.4, 303.0], [2.5, 304.0], [2.6, 304.0], [2.7, 306.0], [2.8, 307.0], [2.9, 307.0], [3.0, 308.0], [3.1, 309.0], [3.2, 310.0], [3.3, 310.0], [3.4, 310.0], [3.5, 310.0], [3.6, 311.0], [3.7, 311.0], [3.8, 311.0], [3.9, 311.0], [4.0, 312.0], [4.1, 312.0], [4.2, 312.0], [4.3, 313.0], [4.4, 313.0], [4.5, 313.0], [4.6, 314.0], [4.7, 314.0], [4.8, 314.0], [4.9, 314.0], [5.0, 315.0], [5.1, 315.0], [5.2, 315.0], [5.3, 315.0], [5.4, 315.0], [5.5, 316.0], [5.6, 316.0], [5.7, 316.0], [5.8, 316.0], [5.9, 316.0], [6.0, 316.0], [6.1, 317.0], [6.2, 317.0], [6.3, 317.0], [6.4, 317.0], [6.5, 317.0], [6.6, 317.0], [6.7, 317.0], [6.8, 317.0], [6.9, 317.0], [7.0, 318.0], [7.1, 318.0], [7.2, 318.0], [7.3, 318.0], [7.4, 318.0], [7.5, 318.0], [7.6, 319.0], [7.7, 319.0], [7.8, 319.0], [7.9, 319.0], [8.0, 319.0], [8.1, 319.0], [8.2, 319.0], [8.3, 319.0], [8.4, 319.0], [8.5, 319.0], [8.6, 320.0], [8.7, 320.0], [8.8, 320.0], [8.9, 320.0], [9.0, 320.0], [9.1, 320.0], [9.2, 320.0], [9.3, 320.0], [9.4, 320.0], [9.5, 320.0], [9.6, 320.0], [9.7, 320.0], [9.8, 321.0], [9.9, 321.0], [10.0, 321.0], [10.1, 321.0], [10.2, 321.0], [10.3, 321.0], [10.4, 321.0], [10.5, 321.0], [10.6, 321.0], [10.7, 321.0], [10.8, 321.0], [10.9, 321.0], [11.0, 322.0], [11.1, 322.0], [11.2, 322.0], [11.3, 322.0], [11.4, 322.0], [11.5, 322.0], [11.6, 322.0], [11.7, 322.0], [11.8, 323.0], [11.9, 323.0], [12.0, 323.0], [12.1, 323.0], [12.2, 323.0], [12.3, 323.0], [12.4, 323.0], [12.5, 323.0], [12.6, 323.0], [12.7, 323.0], [12.8, 323.0], [12.9, 324.0], [13.0, 324.0], [13.1, 324.0], [13.2, 324.0], [13.3, 324.0], [13.4, 324.0], [13.5, 324.0], [13.6, 324.0], [13.7, 324.0], [13.8, 324.0], [13.9, 324.0], [14.0, 325.0], [14.1, 325.0], [14.2, 325.0], [14.3, 325.0], [14.4, 325.0], [14.5, 325.0], [14.6, 325.0], [14.7, 325.0], [14.8, 325.0], [14.9, 325.0], [15.0, 326.0], [15.1, 326.0], [15.2, 326.0], [15.3, 326.0], [15.4, 326.0], [15.5, 326.0], [15.6, 326.0], [15.7, 326.0], [15.8, 326.0], [15.9, 326.0], [16.0, 326.0], [16.1, 326.0], [16.2, 327.0], [16.3, 327.0], [16.4, 327.0], [16.5, 327.0], [16.6, 327.0], [16.7, 327.0], [16.8, 327.0], [16.9, 327.0], [17.0, 327.0], [17.1, 327.0], [17.2, 327.0], [17.3, 327.0], [17.4, 327.0], [17.5, 327.0], [17.6, 328.0], [17.7, 328.0], [17.8, 328.0], [17.9, 328.0], [18.0, 328.0], [18.1, 328.0], [18.2, 328.0], [18.3, 328.0], [18.4, 328.0], [18.5, 328.0], [18.6, 328.0], [18.7, 328.0], [18.8, 328.0], [18.9, 328.0], [19.0, 329.0], [19.1, 329.0], [19.2, 329.0], [19.3, 329.0], [19.4, 329.0], [19.5, 329.0], [19.6, 329.0], [19.7, 329.0], [19.8, 329.0], [19.9, 329.0], [20.0, 329.0], [20.1, 329.0], [20.2, 329.0], [20.3, 329.0], [20.4, 329.0], [20.5, 329.0], [20.6, 329.0], [20.7, 330.0], [20.8, 330.0], [20.9, 330.0], [21.0, 330.0], [21.1, 330.0], [21.2, 330.0], [21.3, 330.0], [21.4, 330.0], [21.5, 330.0], [21.6, 330.0], [21.7, 330.0], [21.8, 330.0], [21.9, 330.0], [22.0, 330.0], [22.1, 330.0], [22.2, 330.0], [22.3, 330.0], [22.4, 331.0], [22.5, 331.0], [22.6, 331.0], [22.7, 331.0], [22.8, 331.0], [22.9, 331.0], [23.0, 331.0], [23.1, 331.0], [23.2, 331.0], [23.3, 331.0], [23.4, 331.0], [23.5, 331.0], [23.6, 331.0], [23.7, 331.0], [23.8, 331.0], [23.9, 331.0], [24.0, 331.0], [24.1, 332.0], [24.2, 332.0], [24.3, 332.0], [24.4, 332.0], [24.5, 332.0], [24.6, 332.0], [24.7, 332.0], [24.8, 332.0], [24.9, 332.0], [25.0, 332.0], [25.1, 332.0], [25.2, 332.0], [25.3, 332.0], [25.4, 332.0], [25.5, 332.0], [25.6, 332.0], [25.7, 333.0], [25.8, 333.0], [25.9, 333.0], [26.0, 333.0], [26.1, 333.0], [26.2, 333.0], [26.3, 333.0], [26.4, 333.0], [26.5, 333.0], [26.6, 334.0], [26.7, 334.0], [26.8, 334.0], [26.9, 334.0], [27.0, 334.0], [27.1, 334.0], [27.2, 334.0], [27.3, 334.0], [27.4, 334.0], [27.5, 334.0], [27.6, 334.0], [27.7, 334.0], [27.8, 334.0], [27.9, 334.0], [28.0, 334.0], [28.1, 334.0], [28.2, 334.0], [28.3, 335.0], [28.4, 335.0], [28.5, 335.0], [28.6, 335.0], [28.7, 335.0], [28.8, 335.0], [28.9, 335.0], [29.0, 335.0], [29.1, 335.0], [29.2, 335.0], [29.3, 335.0], [29.4, 335.0], [29.5, 335.0], [29.6, 336.0], [29.7, 336.0], [29.8, 336.0], [29.9, 336.0], [30.0, 336.0], [30.1, 336.0], [30.2, 336.0], [30.3, 336.0], [30.4, 336.0], [30.5, 336.0], [30.6, 336.0], [30.7, 336.0], [30.8, 336.0], [30.9, 336.0], [31.0, 337.0], [31.1, 337.0], [31.2, 337.0], [31.3, 337.0], [31.4, 337.0], [31.5, 337.0], [31.6, 337.0], [31.7, 337.0], [31.8, 337.0], [31.9, 337.0], [32.0, 337.0], [32.1, 337.0], [32.2, 337.0], [32.3, 338.0], [32.4, 338.0], [32.5, 338.0], [32.6, 338.0], [32.7, 338.0], [32.8, 338.0], [32.9, 338.0], [33.0, 338.0], [33.1, 338.0], [33.2, 338.0], [33.3, 338.0], [33.4, 338.0], [33.5, 338.0], [33.6, 338.0], [33.7, 338.0], [33.8, 338.0], [33.9, 338.0], [34.0, 338.0], [34.1, 339.0], [34.2, 339.0], [34.3, 339.0], [34.4, 339.0], [34.5, 339.0], [34.6, 339.0], [34.7, 339.0], [34.8, 339.0], [34.9, 339.0], [35.0, 339.0], [35.1, 339.0], [35.2, 339.0], [35.3, 339.0], [35.4, 339.0], [35.5, 339.0], [35.6, 340.0], [35.7, 340.0], [35.8, 340.0], [35.9, 340.0], [36.0, 340.0], [36.1, 340.0], [36.2, 340.0], [36.3, 340.0], [36.4, 340.0], [36.5, 340.0], [36.6, 340.0], [36.7, 340.0], [36.8, 340.0], [36.9, 341.0], [37.0, 341.0], [37.1, 341.0], [37.2, 341.0], [37.3, 341.0], [37.4, 341.0], [37.5, 341.0], [37.6, 341.0], [37.7, 341.0], [37.8, 341.0], [37.9, 341.0], [38.0, 341.0], [38.1, 341.0], [38.2, 341.0], [38.3, 341.0], [38.4, 341.0], [38.5, 342.0], [38.6, 342.0], [38.7, 342.0], [38.8, 342.0], [38.9, 342.0], [39.0, 342.0], [39.1, 342.0], [39.2, 342.0], [39.3, 342.0], [39.4, 342.0], [39.5, 342.0], [39.6, 342.0], [39.7, 342.0], [39.8, 342.0], [39.9, 342.0], [40.0, 342.0], [40.1, 342.0], [40.2, 342.0], [40.3, 342.0], [40.4, 342.0], [40.5, 342.0], [40.6, 343.0], [40.7, 343.0], [40.8, 343.0], [40.9, 343.0], [41.0, 343.0], [41.1, 343.0], [41.2, 343.0], [41.3, 343.0], [41.4, 343.0], [41.5, 343.0], [41.6, 343.0], [41.7, 343.0], [41.8, 343.0], [41.9, 343.0], [42.0, 343.0], [42.1, 344.0], [42.2, 344.0], [42.3, 344.0], [42.4, 344.0], [42.5, 344.0], [42.6, 344.0], [42.7, 344.0], [42.8, 344.0], [42.9, 344.0], [43.0, 344.0], [43.1, 344.0], [43.2, 344.0], [43.3, 344.0], [43.4, 344.0], [43.5, 344.0], [43.6, 345.0], [43.7, 345.0], [43.8, 345.0], [43.9, 345.0], [44.0, 345.0], [44.1, 345.0], [44.2, 345.0], [44.3, 345.0], [44.4, 345.0], [44.5, 345.0], [44.6, 345.0], [44.7, 345.0], [44.8, 345.0], [44.9, 345.0], [45.0, 346.0], [45.1, 346.0], [45.2, 346.0], [45.3, 346.0], [45.4, 346.0], [45.5, 346.0], [45.6, 346.0], [45.7, 346.0], [45.8, 346.0], [45.9, 346.0], [46.0, 346.0], [46.1, 346.0], [46.2, 346.0], [46.3, 346.0], [46.4, 346.0], [46.5, 346.0], [46.6, 347.0], [46.7, 347.0], [46.8, 347.0], [46.9, 347.0], [47.0, 347.0], [47.1, 347.0], [47.2, 347.0], [47.3, 347.0], [47.4, 347.0], [47.5, 347.0], [47.6, 347.0], [47.7, 347.0], [47.8, 347.0], [47.9, 347.0], [48.0, 347.0], [48.1, 347.0], [48.2, 348.0], [48.3, 348.0], [48.4, 348.0], [48.5, 348.0], [48.6, 348.0], [48.7, 348.0], [48.8, 348.0], [48.9, 348.0], [49.0, 348.0], [49.1, 348.0], [49.2, 348.0], [49.3, 349.0], [49.4, 349.0], [49.5, 349.0], [49.6, 349.0], [49.7, 349.0], [49.8, 349.0], [49.9, 349.0], [50.0, 349.0], [50.1, 349.0], [50.2, 349.0], [50.3, 350.0], [50.4, 350.0], [50.5, 350.0], [50.6, 350.0], [50.7, 350.0], [50.8, 350.0], [50.9, 350.0], [51.0, 350.0], [51.1, 350.0], [51.2, 350.0], [51.3, 350.0], [51.4, 350.0], [51.5, 350.0], [51.6, 350.0], [51.7, 351.0], [51.8, 351.0], [51.9, 351.0], [52.0, 351.0], [52.1, 351.0], [52.2, 351.0], [52.3, 351.0], [52.4, 351.0], [52.5, 351.0], [52.6, 351.0], [52.7, 351.0], [52.8, 351.0], [52.9, 351.0], [53.0, 351.0], [53.1, 351.0], [53.2, 352.0], [53.3, 352.0], [53.4, 352.0], [53.5, 352.0], [53.6, 352.0], [53.7, 352.0], [53.8, 352.0], [53.9, 352.0], [54.0, 352.0], [54.1, 352.0], [54.2, 352.0], [54.3, 352.0], [54.4, 352.0], [54.5, 352.0], [54.6, 352.0], [54.7, 352.0], [54.8, 353.0], [54.9, 353.0], [55.0, 353.0], [55.1, 353.0], [55.2, 353.0], [55.3, 353.0], [55.4, 353.0], [55.5, 353.0], [55.6, 353.0], [55.7, 353.0], [55.8, 353.0], [55.9, 353.0], [56.0, 353.0], [56.1, 353.0], [56.2, 353.0], [56.3, 354.0], [56.4, 354.0], [56.5, 354.0], [56.6, 354.0], [56.7, 354.0], [56.8, 354.0], [56.9, 354.0], [57.0, 354.0], [57.1, 354.0], [57.2, 354.0], [57.3, 354.0], [57.4, 354.0], [57.5, 354.0], [57.6, 355.0], [57.7, 355.0], [57.8, 355.0], [57.9, 355.0], [58.0, 355.0], [58.1, 355.0], [58.2, 355.0], [58.3, 356.0], [58.4, 356.0], [58.5, 356.0], [58.6, 356.0], [58.7, 356.0], [58.8, 356.0], [58.9, 356.0], [59.0, 356.0], [59.1, 356.0], [59.2, 356.0], [59.3, 356.0], [59.4, 356.0], [59.5, 356.0], [59.6, 356.0], [59.7, 356.0], [59.8, 357.0], [59.9, 357.0], [60.0, 357.0], [60.1, 357.0], [60.2, 357.0], [60.3, 357.0], [60.4, 357.0], [60.5, 357.0], [60.6, 357.0], [60.7, 357.0], [60.8, 358.0], [60.9, 358.0], [61.0, 358.0], [61.1, 358.0], [61.2, 358.0], [61.3, 358.0], [61.4, 358.0], [61.5, 358.0], [61.6, 358.0], [61.7, 358.0], [61.8, 359.0], [61.9, 359.0], [62.0, 359.0], [62.1, 359.0], [62.2, 359.0], [62.3, 359.0], [62.4, 359.0], [62.5, 359.0], [62.6, 359.0], [62.7, 359.0], [62.8, 359.0], [62.9, 360.0], [63.0, 360.0], [63.1, 360.0], [63.2, 360.0], [63.3, 360.0], [63.4, 360.0], [63.5, 360.0], [63.6, 360.0], [63.7, 360.0], [63.8, 360.0], [63.9, 361.0], [64.0, 361.0], [64.1, 361.0], [64.2, 361.0], [64.3, 361.0], [64.4, 361.0], [64.5, 361.0], [64.6, 361.0], [64.7, 361.0], [64.8, 361.0], [64.9, 361.0], [65.0, 362.0], [65.1, 362.0], [65.2, 362.0], [65.3, 362.0], [65.4, 362.0], [65.5, 362.0], [65.6, 362.0], [65.7, 362.0], [65.8, 362.0], [65.9, 363.0], [66.0, 363.0], [66.1, 363.0], [66.2, 363.0], [66.3, 363.0], [66.4, 363.0], [66.5, 363.0], [66.6, 363.0], [66.7, 363.0], [66.8, 363.0], [66.9, 364.0], [67.0, 364.0], [67.1, 364.0], [67.2, 364.0], [67.3, 364.0], [67.4, 365.0], [67.5, 365.0], [67.6, 365.0], [67.7, 365.0], [67.8, 365.0], [67.9, 365.0], [68.0, 365.0], [68.1, 365.0], [68.2, 366.0], [68.3, 366.0], [68.4, 366.0], [68.5, 366.0], [68.6, 366.0], [68.7, 366.0], [68.8, 366.0], [68.9, 366.0], [69.0, 366.0], [69.1, 366.0], [69.2, 366.0], [69.3, 366.0], [69.4, 367.0], [69.5, 367.0], [69.6, 367.0], [69.7, 367.0], [69.8, 367.0], [69.9, 367.0], [70.0, 367.0], [70.1, 367.0], [70.2, 368.0], [70.3, 368.0], [70.4, 368.0], [70.5, 368.0], [70.6, 368.0], [70.7, 369.0], [70.8, 369.0], [70.9, 369.0], [71.0, 369.0], [71.1, 369.0], [71.2, 370.0], [71.3, 370.0], [71.4, 370.0], [71.5, 370.0], [71.6, 370.0], [71.7, 370.0], [71.8, 371.0], [71.9, 371.0], [72.0, 371.0], [72.1, 371.0], [72.2, 371.0], [72.3, 371.0], [72.4, 372.0], [72.5, 372.0], [72.6, 372.0], [72.7, 372.0], [72.8, 372.0], [72.9, 373.0], [73.0, 373.0], [73.1, 373.0], [73.2, 373.0], [73.3, 374.0], [73.4, 374.0], [73.5, 374.0], [73.6, 374.0], [73.7, 375.0], [73.8, 375.0], [73.9, 375.0], [74.0, 375.0], [74.1, 375.0], [74.2, 376.0], [74.3, 376.0], [74.4, 376.0], [74.5, 376.0], [74.6, 376.0], [74.7, 376.0], [74.8, 377.0], [74.9, 377.0], [75.0, 378.0], [75.1, 378.0], [75.2, 378.0], [75.3, 378.0], [75.4, 378.0], [75.5, 379.0], [75.6, 379.0], [75.7, 380.0], [75.8, 380.0], [75.9, 380.0], [76.0, 381.0], [76.1, 381.0], [76.2, 381.0], [76.3, 381.0], [76.4, 381.0], [76.5, 381.0], [76.6, 382.0], [76.7, 382.0], [76.8, 382.0], [76.9, 383.0], [77.0, 383.0], [77.1, 383.0], [77.2, 383.0], [77.3, 384.0], [77.4, 384.0], [77.5, 385.0], [77.6, 385.0], [77.7, 385.0], [77.8, 386.0], [77.9, 387.0], [78.0, 388.0], [78.1, 388.0], [78.2, 388.0], [78.3, 388.0], [78.4, 389.0], [78.5, 390.0], [78.6, 390.0], [78.7, 390.0], [78.8, 390.0], [78.9, 391.0], [79.0, 391.0], [79.1, 392.0], [79.2, 392.0], [79.3, 393.0], [79.4, 394.0], [79.5, 395.0], [79.6, 395.0], [79.7, 396.0], [79.8, 397.0], [79.9, 397.0], [80.0, 398.0], [80.1, 400.0], [80.2, 401.0], [80.3, 401.0], [80.4, 403.0], [80.5, 406.0], [80.6, 408.0], [80.7, 410.0], [80.8, 413.0], [80.9, 414.0], [81.0, 415.0], [81.1, 417.0], [81.2, 418.0], [81.3, 420.0], [81.4, 422.0], [81.5, 422.0], [81.6, 423.0], [81.7, 423.0], [81.8, 426.0], [81.9, 428.0], [82.0, 433.0], [82.1, 441.0], [82.2, 450.0], [82.3, 456.0], [82.4, 463.0], [82.5, 482.0], [82.6, 502.0], [82.7, 547.0], [82.8, 554.0], [82.9, 568.0], [83.0, 578.0], [83.1, 583.0], [83.2, 599.0], [83.3, 609.0], [83.4, 616.0], [83.5, 618.0], [83.6, 624.0], [83.7, 630.0], [83.8, 631.0], [83.9, 632.0], [84.0, 633.0], [84.1, 643.0], [84.2, 643.0], [84.3, 646.0], [84.4, 648.0], [84.5, 651.0], [84.6, 651.0], [84.7, 652.0], [84.8, 652.0], [84.9, 656.0], [85.0, 658.0], [85.1, 660.0], [85.2, 661.0], [85.3, 663.0], [85.4, 664.0], [85.5, 667.0], [85.6, 667.0], [85.7, 667.0], [85.8, 667.0], [85.9, 668.0], [86.0, 670.0], [86.1, 671.0], [86.2, 672.0], [86.3, 672.0], [86.4, 674.0], [86.5, 675.0], [86.6, 678.0], [86.7, 679.0], [86.8, 680.0], [86.9, 680.0], [87.0, 682.0], [87.1, 684.0], [87.2, 684.0], [87.3, 685.0], [87.4, 686.0], [87.5, 688.0], [87.6, 688.0], [87.7, 689.0], [87.8, 689.0], [87.9, 691.0], [88.0, 691.0], [88.1, 694.0], [88.2, 694.0], [88.3, 696.0], [88.4, 696.0], [88.5, 698.0], [88.6, 699.0], [88.7, 700.0], [88.8, 701.0], [88.9, 705.0], [89.0, 706.0], [89.1, 706.0], [89.2, 708.0], [89.3, 709.0], [89.4, 710.0], [89.5, 710.0], [89.6, 711.0], [89.7, 711.0], [89.8, 712.0], [89.9, 714.0], [90.0, 715.0], [90.1, 716.0], [90.2, 717.0], [90.3, 717.0], [90.4, 719.0], [90.5, 721.0], [90.6, 722.0], [90.7, 723.0], [90.8, 724.0], [90.9, 725.0], [91.0, 725.0], [91.1, 726.0], [91.2, 727.0], [91.3, 728.0], [91.4, 729.0], [91.5, 731.0], [91.6, 731.0], [91.7, 732.0], [91.8, 735.0], [91.9, 737.0], [92.0, 738.0], [92.1, 740.0], [92.2, 741.0], [92.3, 742.0], [92.4, 743.0], [92.5, 744.0], [92.6, 745.0], [92.7, 746.0], [92.8, 748.0], [92.9, 748.0], [93.0, 749.0], [93.1, 750.0], [93.2, 751.0], [93.3, 752.0], [93.4, 756.0], [93.5, 757.0], [93.6, 757.0], [93.7, 758.0], [93.8, 758.0], [93.9, 760.0], [94.0, 762.0], [94.1, 765.0], [94.2, 766.0], [94.3, 767.0], [94.4, 769.0], [94.5, 770.0], [94.6, 772.0], [94.7, 774.0], [94.8, 776.0], [94.9, 778.0], [95.0, 778.0], [95.1, 780.0], [95.2, 781.0], [95.3, 783.0], [95.4, 784.0], [95.5, 786.0], [95.6, 789.0], [95.7, 794.0], [95.8, 795.0], [95.9, 798.0], [96.0, 798.0], [96.1, 801.0], [96.2, 805.0], [96.3, 808.0], [96.4, 808.0], [96.5, 811.0], [96.6, 812.0], [96.7, 816.0], [96.8, 816.0], [96.9, 817.0], [97.0, 820.0], [97.1, 824.0], [97.2, 824.0], [97.3, 824.0], [97.4, 832.0], [97.5, 835.0], [97.6, 839.0], [97.7, 846.0], [97.8, 851.0], [97.9, 854.0], [98.0, 854.0], [98.1, 857.0], [98.2, 859.0], [98.3, 863.0], [98.4, 872.0], [98.5, 876.0], [98.6, 880.0], [98.7, 881.0], [98.8, 885.0], [98.9, 889.0], [99.0, 895.0], [99.1, 915.0], [99.2, 933.0], [99.3, 938.0], [99.4, 952.0], [99.5, 955.0], [99.6, 971.0], [99.7, 1003.0], [99.8, 1031.0], [99.9, 1146.0]], "isOverall": false, "label": "HTTP请求", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 100.0, "title": "Response Time Percentiles"}},
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
        data: {"result": {"minY": 3.0, "minX": 200.0, "maxY": 1554.0, "series": [{"data": [[1100.0, 3.0], [300.0, 1554.0], [600.0, 109.0], [700.0, 148.0], [200.0, 47.0], [400.0, 51.0], [800.0, 59.0], [900.0, 13.0], [1000.0, 3.0], [500.0, 13.0]], "isOverall": false, "label": "HTTP请求", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 100, "maxX": 1100.0, "title": "Response Time Distribution"}},
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
        data: {"result": {"minY": 348.0, "minX": 0.0, "ticks": [[0, "Requests having \nresponse time <= 500ms"], [1, "Requests having \nresponse time > 500ms and <= 1,500ms"], [2, "Requests having \nresponse time > 1,500ms"], [3, "Requests in error"]], "maxY": 1652.0, "series": [{"data": [[0.0, 1652.0]], "color": "#9ACD32", "isOverall": false, "label": "Requests having \nresponse time <= 500ms", "isController": false}, {"data": [[1.0, 348.0]], "color": "yellow", "isOverall": false, "label": "Requests having \nresponse time > 500ms and <= 1,500ms", "isController": false}, {"data": [], "color": "orange", "isOverall": false, "label": "Requests having \nresponse time > 1,500ms", "isController": false}, {"data": [], "color": "#FF6347", "isOverall": false, "label": "Requests in error", "isController": false}], "supportsControllersDiscrimination": false, "maxX": 1.0, "title": "Synthetic Response Times Distribution"}},
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
        data: {"result": {"minY": 16.517460317460312, "minX": 1.79317056E12, "maxY": 19.91513353115724, "series": [{"data": [[1.79317062E12, 16.517460317460312], [1.79317056E12, 19.91513353115724]], "isOverall": false, "label": "线程组", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79317062E12, "title": "Active Threads Over Time"}},
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
        data: {"result": {"minY": 245.0, "minX": 1.0, "maxY": 422.22032967032897, "series": [{"data": [[8.0, 266.0], [2.0, 245.0], [9.0, 266.5], [10.0, 301.8888888888889], [11.0, 316.8333333333333], [12.0, 341.66666666666663], [3.0, 264.8571428571429], [13.0, 300.25], [14.0, 350.55555555555554], [15.0, 341.4516129032259], [16.0, 343.71874999999994], [4.0, 282.0], [1.0, 249.25], [17.0, 404.2941176470588], [18.0, 365.57142857142856], [19.0, 392.6666666666667], [5.0, 282.8333333333333], [20.0, 422.22032967032897], [6.0, 268.6666666666667], [7.0, 273.0]], "isOverall": false, "label": "HTTP请求", "isController": false}, {"data": [[19.379999999999963, 414.36799999999965]], "isOverall": false, "label": "HTTP请求-Aggregated", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 20.0, "title": "Time VS Threads"}},
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
        data : {"result": {"minY": 1228.5, "minX": 1.79317056E12, "maxY": 36030.916666666664, "series": [{"data": [[1.79317062E12, 6735.75], [1.79317056E12, 36030.916666666664]], "isOverall": false, "label": "Bytes received per second", "isController": false}, {"data": [[1.79317062E12, 1228.5], [1.79317056E12, 6571.5]], "isOverall": false, "label": "Bytes sent per second", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79317062E12, "title": "Bytes Throughput Over Time"}},
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
        data: {"result": {"minY": 375.0285714285715, "minX": 1.79317056E12, "maxY": 421.7222551928785, "series": [{"data": [[1.79317062E12, 375.0285714285715], [1.79317056E12, 421.7222551928785]], "isOverall": false, "label": "HTTP请求", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79317062E12, "title": "Response Time Over Time"}},
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
        data: {"result": {"minY": 374.9523809523809, "minX": 1.79317056E12, "maxY": 421.58753709198845, "series": [{"data": [[1.79317062E12, 374.9523809523809], [1.79317056E12, 421.58753709198845]], "isOverall": false, "label": "HTTP请求", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79317062E12, "title": "Latencies Over Time"}},
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
        data: {"result": {"minY": 0.939682539682539, "minX": 1.79317056E12, "maxY": 1.2913946587537082, "series": [{"data": [[1.79317062E12, 0.939682539682539], [1.79317056E12, 1.2913946587537082]], "isOverall": false, "label": "HTTP请求", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79317062E12, "title": "Connect Time Over Time"}},
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
        data: {"result": {"minY": 244.0, "minX": 1.79317056E12, "maxY": 1147.0, "series": [{"data": [[1.79317062E12, 895.0], [1.79317056E12, 1147.0]], "isOverall": false, "label": "Max", "isController": false}, {"data": [[1.79317062E12, 245.0], [1.79317056E12, 244.0]], "isOverall": false, "label": "Min", "isController": false}, {"data": [[1.79317062E12, 581.8000000000001], [1.79317056E12, 723.4000000000001]], "isOverall": false, "label": "90th percentile", "isController": false}, {"data": [[1.79317062E12, 844.119999999999], [1.79317056E12, 922.6799999999985]], "isOverall": false, "label": "99th percentile", "isController": false}, {"data": [[1.79317062E12, 339.0], [1.79317056E12, 351.0]], "isOverall": false, "label": "Median", "isController": false}, {"data": [[1.79317062E12, 726.1999999999999], [1.79317056E12, 788.6999999999998]], "isOverall": false, "label": "95th percentile", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79317062E12, "title": "Response Time Percentiles Over Time (successful requests only)"}},
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
    data: {"result": {"minY": 245.0, "minX": 1.0, "maxY": 766.0, "series": [{"data": [[33.0, 306.0], [8.0, 251.5], [40.0, 342.0], [42.0, 375.5], [43.0, 370.0], [45.0, 356.0], [44.0, 352.5], [46.0, 353.0], [47.0, 349.0], [48.0, 351.0], [49.0, 347.0], [51.0, 344.0], [50.0, 341.0], [52.0, 353.0], [1.0, 245.0], [26.0, 286.5], [31.0, 766.0]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 52.0, "title": "Response Time Vs Request"}},
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
    data: {"result": {"minY": 245.0, "minX": 1.0, "maxY": 766.0, "series": [{"data": [[33.0, 306.0], [8.0, 251.5], [40.0, 341.0], [42.0, 375.0], [43.0, 370.0], [45.0, 356.0], [44.0, 352.0], [46.0, 353.0], [47.0, 349.0], [48.0, 351.0], [49.0, 347.0], [51.0, 344.0], [50.0, 341.0], [52.0, 353.0], [1.0, 245.0], [26.0, 286.5], [31.0, 766.0]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 52.0, "title": "Latencies Vs Request"}},
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
        data: {"result": {"minY": 4.916666666666667, "minX": 1.79317056E12, "maxY": 28.416666666666668, "series": [{"data": [[1.79317062E12, 4.916666666666667], [1.79317056E12, 28.416666666666668]], "isOverall": false, "label": "hitsPerSecond", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79317062E12, "title": "Hits Per Second"}},
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
        data: {"result": {"minY": 5.25, "minX": 1.79317056E12, "maxY": 28.083333333333332, "series": [{"data": [[1.79317062E12, 5.25], [1.79317056E12, 28.083333333333332]], "isOverall": false, "label": "200", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79317062E12, "title": "Codes Per Second"}},
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
        data: {"result": {"minY": 5.25, "minX": 1.79317056E12, "maxY": 28.083333333333332, "series": [{"data": [[1.79317062E12, 5.25], [1.79317056E12, 28.083333333333332]], "isOverall": false, "label": "HTTP请求-success", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79317062E12, "title": "Transactions Per Second"}},
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
        data: {"result": {"minY": 5.25, "minX": 1.79317056E12, "maxY": 28.083333333333332, "series": [{"data": [[1.79317062E12, 5.25], [1.79317056E12, 28.083333333333332]], "isOverall": false, "label": "Transaction-success", "isController": false}, {"data": [], "isOverall": false, "label": "Transaction-failure", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79317062E12, "title": "Total Transactions Per Second"}},
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

