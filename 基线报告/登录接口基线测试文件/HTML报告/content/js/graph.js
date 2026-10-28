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
        data: {"result": {"minY": 284.0, "minX": 0.0, "maxY": 1665.0, "series": [{"data": [[0.0, 284.0], [0.1, 294.0], [0.2, 301.0], [0.3, 310.0], [0.4, 322.0], [0.5, 363.0], [0.6, 399.0], [0.7, 412.0], [0.8, 420.0], [0.9, 452.0], [1.0, 476.0], [1.1, 477.0], [1.2, 483.0], [1.3, 490.0], [1.4, 496.0], [1.5, 496.0], [1.6, 500.0], [1.7, 502.0], [1.8, 503.0], [1.9, 504.0], [2.0, 505.0], [2.1, 505.0], [2.2, 505.0], [2.3, 506.0], [2.4, 506.0], [2.5, 507.0], [2.6, 508.0], [2.7, 508.0], [2.8, 509.0], [2.9, 509.0], [3.0, 509.0], [3.1, 509.0], [3.2, 510.0], [3.3, 510.0], [3.4, 511.0], [3.5, 511.0], [3.6, 513.0], [3.7, 513.0], [3.8, 513.0], [3.9, 513.0], [4.0, 514.0], [4.1, 514.0], [4.2, 514.0], [4.3, 515.0], [4.4, 515.0], [4.5, 515.0], [4.6, 516.0], [4.7, 516.0], [4.8, 517.0], [4.9, 518.0], [5.0, 518.0], [5.1, 518.0], [5.2, 519.0], [5.3, 519.0], [5.4, 519.0], [5.5, 519.0], [5.6, 519.0], [5.7, 520.0], [5.8, 520.0], [5.9, 520.0], [6.0, 520.0], [6.1, 520.0], [6.2, 521.0], [6.3, 521.0], [6.4, 521.0], [6.5, 521.0], [6.6, 522.0], [6.7, 522.0], [6.8, 522.0], [6.9, 522.0], [7.0, 522.0], [7.1, 522.0], [7.2, 523.0], [7.3, 523.0], [7.4, 523.0], [7.5, 523.0], [7.6, 523.0], [7.7, 524.0], [7.8, 524.0], [7.9, 524.0], [8.0, 524.0], [8.1, 524.0], [8.2, 524.0], [8.3, 524.0], [8.4, 525.0], [8.5, 525.0], [8.6, 525.0], [8.7, 526.0], [8.8, 526.0], [8.9, 526.0], [9.0, 526.0], [9.1, 526.0], [9.2, 526.0], [9.3, 526.0], [9.4, 526.0], [9.5, 526.0], [9.6, 527.0], [9.7, 527.0], [9.8, 527.0], [9.9, 527.0], [10.0, 527.0], [10.1, 527.0], [10.2, 527.0], [10.3, 527.0], [10.4, 527.0], [10.5, 528.0], [10.6, 528.0], [10.7, 528.0], [10.8, 528.0], [10.9, 528.0], [11.0, 529.0], [11.1, 529.0], [11.2, 529.0], [11.3, 529.0], [11.4, 529.0], [11.5, 529.0], [11.6, 529.0], [11.7, 530.0], [11.8, 530.0], [11.9, 530.0], [12.0, 530.0], [12.1, 530.0], [12.2, 530.0], [12.3, 530.0], [12.4, 530.0], [12.5, 530.0], [12.6, 531.0], [12.7, 531.0], [12.8, 531.0], [12.9, 531.0], [13.0, 531.0], [13.1, 531.0], [13.2, 531.0], [13.3, 531.0], [13.4, 531.0], [13.5, 532.0], [13.6, 532.0], [13.7, 532.0], [13.8, 532.0], [13.9, 532.0], [14.0, 532.0], [14.1, 532.0], [14.2, 533.0], [14.3, 533.0], [14.4, 533.0], [14.5, 533.0], [14.6, 533.0], [14.7, 534.0], [14.8, 534.0], [14.9, 534.0], [15.0, 534.0], [15.1, 534.0], [15.2, 534.0], [15.3, 534.0], [15.4, 535.0], [15.5, 535.0], [15.6, 535.0], [15.7, 535.0], [15.8, 535.0], [15.9, 535.0], [16.0, 535.0], [16.1, 536.0], [16.2, 536.0], [16.3, 536.0], [16.4, 536.0], [16.5, 536.0], [16.6, 537.0], [16.7, 537.0], [16.8, 537.0], [16.9, 537.0], [17.0, 537.0], [17.1, 537.0], [17.2, 538.0], [17.3, 538.0], [17.4, 538.0], [17.5, 538.0], [17.6, 538.0], [17.7, 538.0], [17.8, 538.0], [17.9, 539.0], [18.0, 539.0], [18.1, 539.0], [18.2, 539.0], [18.3, 539.0], [18.4, 539.0], [18.5, 539.0], [18.6, 539.0], [18.7, 540.0], [18.8, 540.0], [18.9, 540.0], [19.0, 540.0], [19.1, 541.0], [19.2, 541.0], [19.3, 541.0], [19.4, 541.0], [19.5, 541.0], [19.6, 541.0], [19.7, 541.0], [19.8, 541.0], [19.9, 541.0], [20.0, 542.0], [20.1, 542.0], [20.2, 542.0], [20.3, 542.0], [20.4, 542.0], [20.5, 542.0], [20.6, 542.0], [20.7, 542.0], [20.8, 542.0], [20.9, 542.0], [21.0, 543.0], [21.1, 543.0], [21.2, 543.0], [21.3, 543.0], [21.4, 543.0], [21.5, 543.0], [21.6, 543.0], [21.7, 543.0], [21.8, 543.0], [21.9, 544.0], [22.0, 544.0], [22.1, 544.0], [22.2, 544.0], [22.3, 544.0], [22.4, 544.0], [22.5, 544.0], [22.6, 544.0], [22.7, 544.0], [22.8, 544.0], [22.9, 544.0], [23.0, 545.0], [23.1, 545.0], [23.2, 545.0], [23.3, 545.0], [23.4, 545.0], [23.5, 545.0], [23.6, 545.0], [23.7, 545.0], [23.8, 545.0], [23.9, 545.0], [24.0, 546.0], [24.1, 546.0], [24.2, 546.0], [24.3, 546.0], [24.4, 546.0], [24.5, 546.0], [24.6, 546.0], [24.7, 546.0], [24.8, 546.0], [24.9, 547.0], [25.0, 547.0], [25.1, 547.0], [25.2, 547.0], [25.3, 547.0], [25.4, 548.0], [25.5, 548.0], [25.6, 548.0], [25.7, 548.0], [25.8, 548.0], [25.9, 548.0], [26.0, 548.0], [26.1, 548.0], [26.2, 549.0], [26.3, 549.0], [26.4, 549.0], [26.5, 549.0], [26.6, 549.0], [26.7, 549.0], [26.8, 549.0], [26.9, 549.0], [27.0, 549.0], [27.1, 549.0], [27.2, 550.0], [27.3, 550.0], [27.4, 550.0], [27.5, 550.0], [27.6, 550.0], [27.7, 550.0], [27.8, 550.0], [27.9, 550.0], [28.0, 550.0], [28.1, 550.0], [28.2, 550.0], [28.3, 550.0], [28.4, 551.0], [28.5, 551.0], [28.6, 551.0], [28.7, 551.0], [28.8, 551.0], [28.9, 551.0], [29.0, 551.0], [29.1, 551.0], [29.2, 551.0], [29.3, 552.0], [29.4, 552.0], [29.5, 552.0], [29.6, 552.0], [29.7, 552.0], [29.8, 552.0], [29.9, 552.0], [30.0, 552.0], [30.1, 552.0], [30.2, 552.0], [30.3, 552.0], [30.4, 552.0], [30.5, 553.0], [30.6, 553.0], [30.7, 553.0], [30.8, 553.0], [30.9, 553.0], [31.0, 553.0], [31.1, 553.0], [31.2, 553.0], [31.3, 553.0], [31.4, 553.0], [31.5, 553.0], [31.6, 553.0], [31.7, 553.0], [31.8, 554.0], [31.9, 554.0], [32.0, 554.0], [32.1, 554.0], [32.2, 554.0], [32.3, 554.0], [32.4, 554.0], [32.5, 554.0], [32.6, 554.0], [32.7, 554.0], [32.8, 554.0], [32.9, 554.0], [33.0, 554.0], [33.1, 555.0], [33.2, 555.0], [33.3, 555.0], [33.4, 555.0], [33.5, 555.0], [33.6, 555.0], [33.7, 555.0], [33.8, 555.0], [33.9, 555.0], [34.0, 555.0], [34.1, 556.0], [34.2, 556.0], [34.3, 556.0], [34.4, 556.0], [34.5, 556.0], [34.6, 556.0], [34.7, 556.0], [34.8, 557.0], [34.9, 557.0], [35.0, 557.0], [35.1, 557.0], [35.2, 557.0], [35.3, 557.0], [35.4, 558.0], [35.5, 558.0], [35.6, 558.0], [35.7, 558.0], [35.8, 558.0], [35.9, 558.0], [36.0, 558.0], [36.1, 558.0], [36.2, 558.0], [36.3, 558.0], [36.4, 559.0], [36.5, 559.0], [36.6, 559.0], [36.7, 559.0], [36.8, 559.0], [36.9, 559.0], [37.0, 559.0], [37.1, 559.0], [37.2, 559.0], [37.3, 560.0], [37.4, 560.0], [37.5, 560.0], [37.6, 560.0], [37.7, 560.0], [37.8, 560.0], [37.9, 560.0], [38.0, 560.0], [38.1, 560.0], [38.2, 561.0], [38.3, 561.0], [38.4, 561.0], [38.5, 561.0], [38.6, 561.0], [38.7, 561.0], [38.8, 561.0], [38.9, 561.0], [39.0, 561.0], [39.1, 561.0], [39.2, 562.0], [39.3, 562.0], [39.4, 562.0], [39.5, 562.0], [39.6, 562.0], [39.7, 562.0], [39.8, 563.0], [39.9, 563.0], [40.0, 563.0], [40.1, 563.0], [40.2, 563.0], [40.3, 563.0], [40.4, 563.0], [40.5, 563.0], [40.6, 563.0], [40.7, 563.0], [40.8, 564.0], [40.9, 564.0], [41.0, 564.0], [41.1, 564.0], [41.2, 564.0], [41.3, 564.0], [41.4, 564.0], [41.5, 564.0], [41.6, 564.0], [41.7, 564.0], [41.8, 565.0], [41.9, 565.0], [42.0, 565.0], [42.1, 565.0], [42.2, 565.0], [42.3, 565.0], [42.4, 565.0], [42.5, 565.0], [42.6, 565.0], [42.7, 565.0], [42.8, 565.0], [42.9, 566.0], [43.0, 566.0], [43.1, 566.0], [43.2, 566.0], [43.3, 566.0], [43.4, 566.0], [43.5, 566.0], [43.6, 566.0], [43.7, 566.0], [43.8, 566.0], [43.9, 567.0], [44.0, 567.0], [44.1, 567.0], [44.2, 567.0], [44.3, 567.0], [44.4, 567.0], [44.5, 568.0], [44.6, 568.0], [44.7, 568.0], [44.8, 568.0], [44.9, 568.0], [45.0, 568.0], [45.1, 568.0], [45.2, 568.0], [45.3, 568.0], [45.4, 568.0], [45.5, 569.0], [45.6, 569.0], [45.7, 569.0], [45.8, 569.0], [45.9, 569.0], [46.0, 569.0], [46.1, 569.0], [46.2, 570.0], [46.3, 570.0], [46.4, 570.0], [46.5, 570.0], [46.6, 570.0], [46.7, 570.0], [46.8, 570.0], [46.9, 570.0], [47.0, 570.0], [47.1, 571.0], [47.2, 571.0], [47.3, 571.0], [47.4, 571.0], [47.5, 571.0], [47.6, 571.0], [47.7, 571.0], [47.8, 571.0], [47.9, 572.0], [48.0, 572.0], [48.1, 572.0], [48.2, 572.0], [48.3, 572.0], [48.4, 572.0], [48.5, 572.0], [48.6, 572.0], [48.7, 573.0], [48.8, 573.0], [48.9, 573.0], [49.0, 573.0], [49.1, 573.0], [49.2, 573.0], [49.3, 573.0], [49.4, 573.0], [49.5, 574.0], [49.6, 574.0], [49.7, 574.0], [49.8, 574.0], [49.9, 574.0], [50.0, 574.0], [50.1, 574.0], [50.2, 574.0], [50.3, 574.0], [50.4, 574.0], [50.5, 574.0], [50.6, 575.0], [50.7, 575.0], [50.8, 575.0], [50.9, 575.0], [51.0, 575.0], [51.1, 575.0], [51.2, 575.0], [51.3, 576.0], [51.4, 576.0], [51.5, 576.0], [51.6, 576.0], [51.7, 576.0], [51.8, 576.0], [51.9, 576.0], [52.0, 576.0], [52.1, 576.0], [52.2, 576.0], [52.3, 576.0], [52.4, 576.0], [52.5, 576.0], [52.6, 577.0], [52.7, 577.0], [52.8, 577.0], [52.9, 577.0], [53.0, 577.0], [53.1, 577.0], [53.2, 577.0], [53.3, 577.0], [53.4, 578.0], [53.5, 578.0], [53.6, 578.0], [53.7, 578.0], [53.8, 578.0], [53.9, 578.0], [54.0, 578.0], [54.1, 578.0], [54.2, 579.0], [54.3, 579.0], [54.4, 579.0], [54.5, 579.0], [54.6, 579.0], [54.7, 579.0], [54.8, 579.0], [54.9, 579.0], [55.0, 580.0], [55.1, 580.0], [55.2, 580.0], [55.3, 580.0], [55.4, 580.0], [55.5, 580.0], [55.6, 580.0], [55.7, 580.0], [55.8, 580.0], [55.9, 581.0], [56.0, 581.0], [56.1, 581.0], [56.2, 581.0], [56.3, 581.0], [56.4, 581.0], [56.5, 581.0], [56.6, 582.0], [56.7, 582.0], [56.8, 582.0], [56.9, 582.0], [57.0, 582.0], [57.1, 582.0], [57.2, 582.0], [57.3, 582.0], [57.4, 582.0], [57.5, 583.0], [57.6, 583.0], [57.7, 583.0], [57.8, 583.0], [57.9, 583.0], [58.0, 583.0], [58.1, 583.0], [58.2, 583.0], [58.3, 583.0], [58.4, 584.0], [58.5, 584.0], [58.6, 584.0], [58.7, 584.0], [58.8, 584.0], [58.9, 584.0], [59.0, 584.0], [59.1, 585.0], [59.2, 585.0], [59.3, 585.0], [59.4, 585.0], [59.5, 585.0], [59.6, 585.0], [59.7, 585.0], [59.8, 585.0], [59.9, 585.0], [60.0, 586.0], [60.1, 586.0], [60.2, 586.0], [60.3, 586.0], [60.4, 586.0], [60.5, 586.0], [60.6, 586.0], [60.7, 586.0], [60.8, 587.0], [60.9, 587.0], [61.0, 587.0], [61.1, 587.0], [61.2, 587.0], [61.3, 587.0], [61.4, 587.0], [61.5, 587.0], [61.6, 588.0], [61.7, 588.0], [61.8, 588.0], [61.9, 588.0], [62.0, 588.0], [62.1, 588.0], [62.2, 589.0], [62.3, 589.0], [62.4, 589.0], [62.5, 589.0], [62.6, 589.0], [62.7, 589.0], [62.8, 589.0], [62.9, 590.0], [63.0, 590.0], [63.1, 590.0], [63.2, 590.0], [63.3, 590.0], [63.4, 590.0], [63.5, 591.0], [63.6, 591.0], [63.7, 591.0], [63.8, 591.0], [63.9, 591.0], [64.0, 591.0], [64.1, 592.0], [64.2, 592.0], [64.3, 592.0], [64.4, 592.0], [64.5, 592.0], [64.6, 592.0], [64.7, 592.0], [64.8, 592.0], [64.9, 593.0], [65.0, 593.0], [65.1, 593.0], [65.2, 593.0], [65.3, 593.0], [65.4, 594.0], [65.5, 594.0], [65.6, 594.0], [65.7, 594.0], [65.8, 594.0], [65.9, 594.0], [66.0, 595.0], [66.1, 595.0], [66.2, 595.0], [66.3, 595.0], [66.4, 596.0], [66.5, 596.0], [66.6, 596.0], [66.7, 596.0], [66.8, 597.0], [66.9, 597.0], [67.0, 597.0], [67.1, 597.0], [67.2, 597.0], [67.3, 598.0], [67.4, 598.0], [67.5, 598.0], [67.6, 598.0], [67.7, 598.0], [67.8, 598.0], [67.9, 598.0], [68.0, 598.0], [68.1, 598.0], [68.2, 598.0], [68.3, 599.0], [68.4, 599.0], [68.5, 599.0], [68.6, 599.0], [68.7, 599.0], [68.8, 599.0], [68.9, 599.0], [69.0, 600.0], [69.1, 600.0], [69.2, 600.0], [69.3, 600.0], [69.4, 600.0], [69.5, 601.0], [69.6, 601.0], [69.7, 601.0], [69.8, 601.0], [69.9, 601.0], [70.0, 602.0], [70.1, 602.0], [70.2, 602.0], [70.3, 602.0], [70.4, 602.0], [70.5, 602.0], [70.6, 603.0], [70.7, 603.0], [70.8, 603.0], [70.9, 603.0], [71.0, 604.0], [71.1, 604.0], [71.2, 604.0], [71.3, 604.0], [71.4, 604.0], [71.5, 604.0], [71.6, 604.0], [71.7, 605.0], [71.8, 605.0], [71.9, 605.0], [72.0, 605.0], [72.1, 605.0], [72.2, 605.0], [72.3, 606.0], [72.4, 606.0], [72.5, 606.0], [72.6, 606.0], [72.7, 607.0], [72.8, 607.0], [72.9, 607.0], [73.0, 607.0], [73.1, 607.0], [73.2, 607.0], [73.3, 607.0], [73.4, 608.0], [73.5, 608.0], [73.6, 608.0], [73.7, 608.0], [73.8, 608.0], [73.9, 609.0], [74.0, 609.0], [74.1, 609.0], [74.2, 610.0], [74.3, 610.0], [74.4, 611.0], [74.5, 611.0], [74.6, 611.0], [74.7, 611.0], [74.8, 611.0], [74.9, 612.0], [75.0, 612.0], [75.1, 612.0], [75.2, 613.0], [75.3, 613.0], [75.4, 613.0], [75.5, 613.0], [75.6, 613.0], [75.7, 613.0], [75.8, 613.0], [75.9, 613.0], [76.0, 614.0], [76.1, 614.0], [76.2, 615.0], [76.3, 615.0], [76.4, 615.0], [76.5, 615.0], [76.6, 616.0], [76.7, 616.0], [76.8, 616.0], [76.9, 616.0], [77.0, 616.0], [77.1, 617.0], [77.2, 617.0], [77.3, 617.0], [77.4, 618.0], [77.5, 618.0], [77.6, 618.0], [77.7, 618.0], [77.8, 618.0], [77.9, 619.0], [78.0, 619.0], [78.1, 619.0], [78.2, 619.0], [78.3, 619.0], [78.4, 620.0], [78.5, 620.0], [78.6, 621.0], [78.7, 621.0], [78.8, 621.0], [78.9, 621.0], [79.0, 621.0], [79.1, 622.0], [79.2, 622.0], [79.3, 622.0], [79.4, 623.0], [79.5, 623.0], [79.6, 624.0], [79.7, 624.0], [79.8, 624.0], [79.9, 625.0], [80.0, 625.0], [80.1, 625.0], [80.2, 625.0], [80.3, 626.0], [80.4, 626.0], [80.5, 626.0], [80.6, 626.0], [80.7, 626.0], [80.8, 627.0], [80.9, 627.0], [81.0, 628.0], [81.1, 628.0], [81.2, 628.0], [81.3, 629.0], [81.4, 629.0], [81.5, 629.0], [81.6, 630.0], [81.7, 630.0], [81.8, 630.0], [81.9, 630.0], [82.0, 631.0], [82.1, 631.0], [82.2, 631.0], [82.3, 632.0], [82.4, 632.0], [82.5, 632.0], [82.6, 632.0], [82.7, 633.0], [82.8, 633.0], [82.9, 633.0], [83.0, 633.0], [83.1, 634.0], [83.2, 634.0], [83.3, 634.0], [83.4, 635.0], [83.5, 636.0], [83.6, 636.0], [83.7, 636.0], [83.8, 637.0], [83.9, 637.0], [84.0, 638.0], [84.1, 638.0], [84.2, 638.0], [84.3, 639.0], [84.4, 639.0], [84.5, 640.0], [84.6, 640.0], [84.7, 640.0], [84.8, 641.0], [84.9, 641.0], [85.0, 642.0], [85.1, 642.0], [85.2, 642.0], [85.3, 642.0], [85.4, 643.0], [85.5, 643.0], [85.6, 644.0], [85.7, 644.0], [85.8, 645.0], [85.9, 645.0], [86.0, 645.0], [86.1, 646.0], [86.2, 646.0], [86.3, 646.0], [86.4, 646.0], [86.5, 647.0], [86.6, 648.0], [86.7, 648.0], [86.8, 649.0], [86.9, 649.0], [87.0, 649.0], [87.1, 650.0], [87.2, 650.0], [87.3, 651.0], [87.4, 651.0], [87.5, 651.0], [87.6, 652.0], [87.7, 652.0], [87.8, 652.0], [87.9, 652.0], [88.0, 653.0], [88.1, 653.0], [88.2, 654.0], [88.3, 655.0], [88.4, 656.0], [88.5, 656.0], [88.6, 656.0], [88.7, 657.0], [88.8, 658.0], [88.9, 658.0], [89.0, 659.0], [89.1, 660.0], [89.2, 660.0], [89.3, 660.0], [89.4, 661.0], [89.5, 662.0], [89.6, 663.0], [89.7, 664.0], [89.8, 665.0], [89.9, 668.0], [90.0, 668.0], [90.1, 670.0], [90.2, 670.0], [90.3, 670.0], [90.4, 671.0], [90.5, 672.0], [90.6, 673.0], [90.7, 673.0], [90.8, 673.0], [90.9, 675.0], [91.0, 675.0], [91.1, 676.0], [91.2, 676.0], [91.3, 677.0], [91.4, 679.0], [91.5, 679.0], [91.6, 680.0], [91.7, 681.0], [91.8, 682.0], [91.9, 683.0], [92.0, 684.0], [92.1, 684.0], [92.2, 686.0], [92.3, 687.0], [92.4, 690.0], [92.5, 691.0], [92.6, 692.0], [92.7, 693.0], [92.8, 697.0], [92.9, 698.0], [93.0, 700.0], [93.1, 700.0], [93.2, 701.0], [93.3, 703.0], [93.4, 705.0], [93.5, 707.0], [93.6, 708.0], [93.7, 708.0], [93.8, 711.0], [93.9, 713.0], [94.0, 718.0], [94.1, 720.0], [94.2, 724.0], [94.3, 725.0], [94.4, 726.0], [94.5, 726.0], [94.6, 728.0], [94.7, 730.0], [94.8, 731.0], [94.9, 733.0], [95.0, 733.0], [95.1, 734.0], [95.2, 735.0], [95.3, 737.0], [95.4, 741.0], [95.5, 742.0], [95.6, 743.0], [95.7, 745.0], [95.8, 751.0], [95.9, 752.0], [96.0, 754.0], [96.1, 755.0], [96.2, 757.0], [96.3, 758.0], [96.4, 761.0], [96.5, 762.0], [96.6, 768.0], [96.7, 770.0], [96.8, 771.0], [96.9, 775.0], [97.0, 776.0], [97.1, 777.0], [97.2, 779.0], [97.3, 781.0], [97.4, 781.0], [97.5, 785.0], [97.6, 787.0], [97.7, 792.0], [97.8, 797.0], [97.9, 801.0], [98.0, 806.0], [98.1, 810.0], [98.2, 812.0], [98.3, 825.0], [98.4, 826.0], [98.5, 827.0], [98.6, 831.0], [98.7, 836.0], [98.8, 862.0], [98.9, 878.0], [99.0, 896.0], [99.1, 902.0], [99.2, 917.0], [99.3, 938.0], [99.4, 955.0], [99.5, 986.0], [99.6, 998.0], [99.7, 1062.0], [99.8, 1569.0], [99.9, 1630.0]], "isOverall": false, "label": "HTTP请求", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 100.0, "title": "Response Time Percentiles"}},
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
        data: {"result": {"minY": 1.0, "minX": 200.0, "maxY": 1348.0, "series": [{"data": [[1100.0, 1.0], [300.0, 9.0], [600.0, 481.0], [700.0, 98.0], [1500.0, 1.0], [200.0, 4.0], [800.0, 24.0], [1600.0, 3.0], [400.0, 18.0], [900.0, 11.0], [1000.0, 2.0], [500.0, 1348.0]], "isOverall": false, "label": "HTTP请求", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 100, "maxX": 1600.0, "title": "Response Time Distribution"}},
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
        data: {"result": {"minY": 4.0, "minX": 0.0, "ticks": [[0, "Requests having \nresponse time <= 500ms"], [1, "Requests having \nresponse time > 500ms and <= 1,500ms"], [2, "Requests having \nresponse time > 1,500ms"], [3, "Requests in error"]], "maxY": 1964.0, "series": [{"data": [[0.0, 32.0]], "color": "#9ACD32", "isOverall": false, "label": "Requests having \nresponse time <= 500ms", "isController": false}, {"data": [[1.0, 1964.0]], "color": "yellow", "isOverall": false, "label": "Requests having \nresponse time > 500ms and <= 1,500ms", "isController": false}, {"data": [[2.0, 4.0]], "color": "orange", "isOverall": false, "label": "Requests having \nresponse time > 1,500ms", "isController": false}, {"data": [], "color": "#FF6347", "isOverall": false, "label": "Requests in error", "isController": false}], "supportsControllersDiscrimination": false, "maxX": 2.0, "title": "Synthetic Response Times Distribution"}},
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
        data: {"result": {"minY": 19.842876165113193, "minX": 1.79315658E12, "maxY": 19.921686746987927, "series": [{"data": [[1.79315658E12, 19.921686746987927], [1.79315664E12, 19.842876165113193]], "isOverall": false, "label": "线程组", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79315664E12, "title": "Active Threads Over Time"}},
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
        data: {"result": {"minY": 291.0, "minX": 1.0, "maxY": 609.0, "series": [{"data": [[8.0, 342.0], [2.0, 318.0], [9.0, 381.0], [10.0, 394.0], [11.0, 356.5], [12.0, 449.0], [3.0, 322.0], [13.0, 459.0], [14.0, 508.5], [15.0, 524.0], [16.0, 542.5], [4.0, 310.0], [1.0, 293.0], [17.0, 535.75], [18.0, 609.0], [19.0, 587.3333333333333], [20.0, 592.7965323814396], [5.0, 294.0], [6.0, 291.0], [7.0, 310.0]], "isOverall": false, "label": "HTTP请求", "isController": false}, {"data": [[19.862500000000015, 590.3994999999995]], "isOverall": false, "label": "HTTP请求-Aggregated", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 20.0, "title": "Time VS Threads"}},
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
        data : {"result": {"minY": 1942.2, "minX": 1.79315658E12, "maxY": 32117.766666666666, "series": [{"data": [[1.79315658E12, 10648.9], [1.79315664E12, 32117.766666666666]], "isOverall": false, "label": "Bytes received per second", "isController": false}, {"data": [[1.79315658E12, 1942.2], [1.79315664E12, 5857.8]], "isOverall": false, "label": "Bytes sent per second", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79315664E12, "title": "Bytes Throughput Over Time"}},
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
        data: {"result": {"minY": 583.8335552596528, "minX": 1.79315658E12, "maxY": 610.2028112449801, "series": [{"data": [[1.79315658E12, 610.2028112449801], [1.79315664E12, 583.8335552596528]], "isOverall": false, "label": "HTTP请求", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79315664E12, "title": "Response Time Over Time"}},
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
        data: {"result": {"minY": 583.7090545938754, "minX": 1.79315658E12, "maxY": 610.0481927710847, "series": [{"data": [[1.79315658E12, 610.0481927710847], [1.79315664E12, 583.7090545938754]], "isOverall": false, "label": "HTTP请求", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79315664E12, "title": "Latencies Over Time"}},
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
        data: {"result": {"minY": 0.8815261044176711, "minX": 1.79315658E12, "maxY": 1.1271637816245017, "series": [{"data": [[1.79315658E12, 0.8815261044176711], [1.79315664E12, 1.1271637816245017]], "isOverall": false, "label": "HTTP请求", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79315664E12, "title": "Connect Time Over Time"}},
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
        data: {"result": {"minY": 284.0, "minX": 1.79315658E12, "maxY": 1665.0, "series": [{"data": [[1.79315658E12, 1665.0], [1.79315664E12, 998.0]], "isOverall": false, "label": "Max", "isController": false}, {"data": [[1.79315658E12, 284.0], [1.79315664E12, 293.0]], "isOverall": false, "label": "Min", "isController": false}, {"data": [[1.79315658E12, 741.4000000000001], [1.79315664E12, 655.0]], "isOverall": false, "label": "90th percentile", "isController": false}, {"data": [[1.79315658E12, 1110.6299999999958], [1.79315664E12, 815.8800000000001]], "isOverall": false, "label": "99th percentile", "isController": false}, {"data": [[1.79315658E12, 582.0], [1.79315664E12, 572.5]], "isOverall": false, "label": "Median", "isController": false}, {"data": [[1.79315658E12, 801.05], [1.79315664E12, 698.0]], "isOverall": false, "label": "95th percentile", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79315664E12, "title": "Response Time Percentiles Over Time (successful requests only)"}},
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
    data: {"result": {"minY": 541.5, "minX": 9.0, "maxY": 825.0, "series": [{"data": [[32.0, 599.0], [33.0, 592.0], [34.0, 580.0], [35.0, 570.0], [9.0, 636.0], [36.0, 553.5], [37.0, 554.0], [38.0, 541.5], [23.0, 726.0], [24.0, 786.5], [25.0, 825.0], [28.0, 821.0], [29.0, 673.0], [30.0, 644.5], [31.0, 639.0]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 38.0, "title": "Response Time Vs Request"}},
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
    data: {"result": {"minY": 541.5, "minX": 9.0, "maxY": 825.0, "series": [{"data": [[32.0, 599.0], [33.0, 592.0], [34.0, 580.0], [35.0, 570.0], [9.0, 636.0], [36.0, 553.5], [37.0, 554.0], [38.0, 541.5], [23.0, 726.0], [24.0, 786.5], [25.0, 825.0], [28.0, 821.0], [29.0, 673.0], [30.0, 644.5], [31.0, 639.0]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 38.0, "title": "Latencies Vs Request"}},
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
        data: {"result": {"minY": 8.633333333333333, "minX": 1.79315658E12, "maxY": 24.7, "series": [{"data": [[1.79315658E12, 8.633333333333333], [1.79315664E12, 24.7]], "isOverall": false, "label": "hitsPerSecond", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79315664E12, "title": "Hits Per Second"}},
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
        data: {"result": {"minY": 8.3, "minX": 1.79315658E12, "maxY": 25.033333333333335, "series": [{"data": [[1.79315658E12, 8.3], [1.79315664E12, 25.033333333333335]], "isOverall": false, "label": "200", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79315664E12, "title": "Codes Per Second"}},
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
        data: {"result": {"minY": 8.3, "minX": 1.79315658E12, "maxY": 25.033333333333335, "series": [{"data": [[1.79315658E12, 8.3], [1.79315664E12, 25.033333333333335]], "isOverall": false, "label": "HTTP请求-success", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79315664E12, "title": "Transactions Per Second"}},
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
        data: {"result": {"minY": 8.3, "minX": 1.79315658E12, "maxY": 25.033333333333335, "series": [{"data": [[1.79315658E12, 8.3], [1.79315664E12, 25.033333333333335]], "isOverall": false, "label": "Transaction-success", "isController": false}, {"data": [], "isOverall": false, "label": "Transaction-failure", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79315664E12, "title": "Total Transactions Per Second"}},
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

