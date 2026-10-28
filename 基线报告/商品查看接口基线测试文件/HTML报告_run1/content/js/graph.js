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
        data: {"result": {"minY": 14.0, "minX": 0.0, "maxY": 1319.0, "series": [{"data": [[0.0, 14.0], [0.1, 15.0], [0.2, 18.0], [0.3, 22.0], [0.4, 27.0], [0.5, 28.0], [0.6, 30.0], [0.7, 33.0], [0.8, 43.0], [0.9, 44.0], [1.0, 47.0], [1.1, 52.0], [1.2, 59.0], [1.3, 64.0], [1.4, 66.0], [1.5, 72.0], [1.6, 73.0], [1.7, 75.0], [1.8, 82.0], [1.9, 85.0], [2.0, 88.0], [2.1, 97.0], [2.2, 99.0], [2.3, 99.0], [2.4, 102.0], [2.5, 104.0], [2.6, 105.0], [2.7, 106.0], [2.8, 109.0], [2.9, 110.0], [3.0, 111.0], [3.1, 111.0], [3.2, 113.0], [3.3, 113.0], [3.4, 113.0], [3.5, 113.0], [3.6, 114.0], [3.7, 116.0], [3.8, 117.0], [3.9, 118.0], [4.0, 118.0], [4.1, 118.0], [4.2, 119.0], [4.3, 120.0], [4.4, 120.0], [4.5, 121.0], [4.6, 122.0], [4.7, 123.0], [4.8, 123.0], [4.9, 123.0], [5.0, 124.0], [5.1, 126.0], [5.2, 126.0], [5.3, 127.0], [5.4, 128.0], [5.5, 128.0], [5.6, 129.0], [5.7, 129.0], [5.8, 130.0], [5.9, 130.0], [6.0, 131.0], [6.1, 131.0], [6.2, 131.0], [6.3, 132.0], [6.4, 133.0], [6.5, 133.0], [6.6, 134.0], [6.7, 135.0], [6.8, 135.0], [6.9, 136.0], [7.0, 136.0], [7.1, 137.0], [7.2, 137.0], [7.3, 137.0], [7.4, 138.0], [7.5, 138.0], [7.6, 139.0], [7.7, 139.0], [7.8, 139.0], [7.9, 140.0], [8.0, 141.0], [8.1, 142.0], [8.2, 142.0], [8.3, 142.0], [8.4, 143.0], [8.5, 143.0], [8.6, 144.0], [8.7, 144.0], [8.8, 144.0], [8.9, 145.0], [9.0, 145.0], [9.1, 146.0], [9.2, 146.0], [9.3, 146.0], [9.4, 146.0], [9.5, 147.0], [9.6, 147.0], [9.7, 147.0], [9.8, 147.0], [9.9, 148.0], [10.0, 149.0], [10.1, 149.0], [10.2, 149.0], [10.3, 149.0], [10.4, 149.0], [10.5, 150.0], [10.6, 150.0], [10.7, 150.0], [10.8, 150.0], [10.9, 150.0], [11.0, 150.0], [11.1, 151.0], [11.2, 151.0], [11.3, 151.0], [11.4, 151.0], [11.5, 151.0], [11.6, 152.0], [11.7, 152.0], [11.8, 153.0], [11.9, 153.0], [12.0, 153.0], [12.1, 153.0], [12.2, 153.0], [12.3, 153.0], [12.4, 154.0], [12.5, 154.0], [12.6, 155.0], [12.7, 155.0], [12.8, 155.0], [12.9, 155.0], [13.0, 155.0], [13.1, 156.0], [13.2, 156.0], [13.3, 156.0], [13.4, 156.0], [13.5, 156.0], [13.6, 157.0], [13.7, 157.0], [13.8, 157.0], [13.9, 157.0], [14.0, 157.0], [14.1, 157.0], [14.2, 158.0], [14.3, 158.0], [14.4, 158.0], [14.5, 158.0], [14.6, 158.0], [14.7, 158.0], [14.8, 158.0], [14.9, 159.0], [15.0, 159.0], [15.1, 159.0], [15.2, 159.0], [15.3, 159.0], [15.4, 160.0], [15.5, 160.0], [15.6, 160.0], [15.7, 160.0], [15.8, 161.0], [15.9, 161.0], [16.0, 161.0], [16.1, 161.0], [16.2, 161.0], [16.3, 161.0], [16.4, 161.0], [16.5, 162.0], [16.6, 162.0], [16.7, 162.0], [16.8, 162.0], [16.9, 162.0], [17.0, 163.0], [17.1, 163.0], [17.2, 163.0], [17.3, 163.0], [17.4, 163.0], [17.5, 163.0], [17.6, 164.0], [17.7, 164.0], [17.8, 164.0], [17.9, 164.0], [18.0, 164.0], [18.1, 164.0], [18.2, 165.0], [18.3, 165.0], [18.4, 165.0], [18.5, 165.0], [18.6, 165.0], [18.7, 165.0], [18.8, 165.0], [18.9, 165.0], [19.0, 166.0], [19.1, 166.0], [19.2, 166.0], [19.3, 166.0], [19.4, 166.0], [19.5, 166.0], [19.6, 166.0], [19.7, 166.0], [19.8, 166.0], [19.9, 166.0], [20.0, 166.0], [20.1, 166.0], [20.2, 166.0], [20.3, 166.0], [20.4, 167.0], [20.5, 167.0], [20.6, 167.0], [20.7, 167.0], [20.8, 167.0], [20.9, 167.0], [21.0, 167.0], [21.1, 167.0], [21.2, 167.0], [21.3, 167.0], [21.4, 167.0], [21.5, 168.0], [21.6, 168.0], [21.7, 168.0], [21.8, 168.0], [21.9, 168.0], [22.0, 169.0], [22.1, 169.0], [22.2, 169.0], [22.3, 169.0], [22.4, 169.0], [22.5, 169.0], [22.6, 169.0], [22.7, 169.0], [22.8, 170.0], [22.9, 170.0], [23.0, 170.0], [23.1, 170.0], [23.2, 170.0], [23.3, 170.0], [23.4, 170.0], [23.5, 170.0], [23.6, 170.0], [23.7, 170.0], [23.8, 171.0], [23.9, 171.0], [24.0, 171.0], [24.1, 171.0], [24.2, 171.0], [24.3, 171.0], [24.4, 171.0], [24.5, 171.0], [24.6, 171.0], [24.7, 171.0], [24.8, 171.0], [24.9, 171.0], [25.0, 172.0], [25.1, 172.0], [25.2, 172.0], [25.3, 172.0], [25.4, 172.0], [25.5, 172.0], [25.6, 172.0], [25.7, 172.0], [25.8, 172.0], [25.9, 173.0], [26.0, 173.0], [26.1, 173.0], [26.2, 173.0], [26.3, 173.0], [26.4, 173.0], [26.5, 173.0], [26.6, 173.0], [26.7, 173.0], [26.8, 173.0], [26.9, 173.0], [27.0, 173.0], [27.1, 173.0], [27.2, 173.0], [27.3, 174.0], [27.4, 174.0], [27.5, 174.0], [27.6, 174.0], [27.7, 174.0], [27.8, 174.0], [27.9, 174.0], [28.0, 174.0], [28.1, 174.0], [28.2, 174.0], [28.3, 175.0], [28.4, 175.0], [28.5, 175.0], [28.6, 175.0], [28.7, 175.0], [28.8, 175.0], [28.9, 175.0], [29.0, 175.0], [29.1, 175.0], [29.2, 176.0], [29.3, 176.0], [29.4, 176.0], [29.5, 176.0], [29.6, 176.0], [29.7, 176.0], [29.8, 176.0], [29.9, 176.0], [30.0, 176.0], [30.1, 176.0], [30.2, 176.0], [30.3, 176.0], [30.4, 176.0], [30.5, 177.0], [30.6, 177.0], [30.7, 177.0], [30.8, 177.0], [30.9, 177.0], [31.0, 177.0], [31.1, 177.0], [31.2, 177.0], [31.3, 177.0], [31.4, 177.0], [31.5, 177.0], [31.6, 177.0], [31.7, 178.0], [31.8, 178.0], [31.9, 178.0], [32.0, 178.0], [32.1, 178.0], [32.2, 178.0], [32.3, 178.0], [32.4, 178.0], [32.5, 178.0], [32.6, 178.0], [32.7, 179.0], [32.8, 179.0], [32.9, 179.0], [33.0, 179.0], [33.1, 179.0], [33.2, 179.0], [33.3, 179.0], [33.4, 179.0], [33.5, 179.0], [33.6, 179.0], [33.7, 179.0], [33.8, 179.0], [33.9, 180.0], [34.0, 180.0], [34.1, 180.0], [34.2, 180.0], [34.3, 180.0], [34.4, 180.0], [34.5, 180.0], [34.6, 180.0], [34.7, 180.0], [34.8, 180.0], [34.9, 180.0], [35.0, 180.0], [35.1, 180.0], [35.2, 181.0], [35.3, 181.0], [35.4, 181.0], [35.5, 181.0], [35.6, 181.0], [35.7, 181.0], [35.8, 181.0], [35.9, 181.0], [36.0, 181.0], [36.1, 181.0], [36.2, 181.0], [36.3, 181.0], [36.4, 181.0], [36.5, 181.0], [36.6, 181.0], [36.7, 182.0], [36.8, 182.0], [36.9, 182.0], [37.0, 182.0], [37.1, 182.0], [37.2, 182.0], [37.3, 182.0], [37.4, 182.0], [37.5, 182.0], [37.6, 182.0], [37.7, 182.0], [37.8, 183.0], [37.9, 183.0], [38.0, 183.0], [38.1, 183.0], [38.2, 183.0], [38.3, 183.0], [38.4, 183.0], [38.5, 183.0], [38.6, 183.0], [38.7, 183.0], [38.8, 183.0], [38.9, 183.0], [39.0, 183.0], [39.1, 183.0], [39.2, 183.0], [39.3, 183.0], [39.4, 183.0], [39.5, 183.0], [39.6, 184.0], [39.7, 184.0], [39.8, 184.0], [39.9, 184.0], [40.0, 184.0], [40.1, 184.0], [40.2, 184.0], [40.3, 184.0], [40.4, 185.0], [40.5, 185.0], [40.6, 185.0], [40.7, 185.0], [40.8, 185.0], [40.9, 185.0], [41.0, 185.0], [41.1, 185.0], [41.2, 185.0], [41.3, 185.0], [41.4, 185.0], [41.5, 186.0], [41.6, 186.0], [41.7, 186.0], [41.8, 186.0], [41.9, 186.0], [42.0, 186.0], [42.1, 186.0], [42.2, 186.0], [42.3, 186.0], [42.4, 186.0], [42.5, 186.0], [42.6, 186.0], [42.7, 186.0], [42.8, 186.0], [42.9, 186.0], [43.0, 186.0], [43.1, 186.0], [43.2, 186.0], [43.3, 187.0], [43.4, 187.0], [43.5, 187.0], [43.6, 187.0], [43.7, 187.0], [43.8, 187.0], [43.9, 187.0], [44.0, 187.0], [44.1, 187.0], [44.2, 187.0], [44.3, 187.0], [44.4, 187.0], [44.5, 188.0], [44.6, 188.0], [44.7, 188.0], [44.8, 188.0], [44.9, 188.0], [45.0, 188.0], [45.1, 188.0], [45.2, 188.0], [45.3, 188.0], [45.4, 188.0], [45.5, 189.0], [45.6, 189.0], [45.7, 189.0], [45.8, 189.0], [45.9, 189.0], [46.0, 189.0], [46.1, 189.0], [46.2, 189.0], [46.3, 189.0], [46.4, 189.0], [46.5, 190.0], [46.6, 190.0], [46.7, 190.0], [46.8, 190.0], [46.9, 190.0], [47.0, 190.0], [47.1, 190.0], [47.2, 190.0], [47.3, 190.0], [47.4, 190.0], [47.5, 190.0], [47.6, 190.0], [47.7, 190.0], [47.8, 190.0], [47.9, 190.0], [48.0, 190.0], [48.1, 190.0], [48.2, 190.0], [48.3, 191.0], [48.4, 191.0], [48.5, 191.0], [48.6, 191.0], [48.7, 191.0], [48.8, 191.0], [48.9, 191.0], [49.0, 191.0], [49.1, 191.0], [49.2, 191.0], [49.3, 191.0], [49.4, 191.0], [49.5, 191.0], [49.6, 191.0], [49.7, 192.0], [49.8, 192.0], [49.9, 192.0], [50.0, 192.0], [50.1, 192.0], [50.2, 192.0], [50.3, 192.0], [50.4, 192.0], [50.5, 192.0], [50.6, 192.0], [50.7, 192.0], [50.8, 192.0], [50.9, 192.0], [51.0, 193.0], [51.1, 193.0], [51.2, 193.0], [51.3, 193.0], [51.4, 193.0], [51.5, 193.0], [51.6, 193.0], [51.7, 193.0], [51.8, 193.0], [51.9, 193.0], [52.0, 193.0], [52.1, 193.0], [52.2, 193.0], [52.3, 193.0], [52.4, 194.0], [52.5, 194.0], [52.6, 194.0], [52.7, 194.0], [52.8, 194.0], [52.9, 194.0], [53.0, 194.0], [53.1, 194.0], [53.2, 194.0], [53.3, 194.0], [53.4, 194.0], [53.5, 195.0], [53.6, 195.0], [53.7, 195.0], [53.8, 195.0], [53.9, 195.0], [54.0, 195.0], [54.1, 195.0], [54.2, 195.0], [54.3, 195.0], [54.4, 195.0], [54.5, 195.0], [54.6, 195.0], [54.7, 196.0], [54.8, 196.0], [54.9, 196.0], [55.0, 196.0], [55.1, 196.0], [55.2, 196.0], [55.3, 196.0], [55.4, 196.0], [55.5, 196.0], [55.6, 196.0], [55.7, 196.0], [55.8, 196.0], [55.9, 197.0], [56.0, 197.0], [56.1, 197.0], [56.2, 197.0], [56.3, 197.0], [56.4, 197.0], [56.5, 197.0], [56.6, 197.0], [56.7, 197.0], [56.8, 197.0], [56.9, 197.0], [57.0, 198.0], [57.1, 198.0], [57.2, 198.0], [57.3, 198.0], [57.4, 198.0], [57.5, 198.0], [57.6, 198.0], [57.7, 198.0], [57.8, 198.0], [57.9, 199.0], [58.0, 199.0], [58.1, 199.0], [58.2, 199.0], [58.3, 199.0], [58.4, 199.0], [58.5, 199.0], [58.6, 199.0], [58.7, 199.0], [58.8, 199.0], [58.9, 200.0], [59.0, 200.0], [59.1, 200.0], [59.2, 200.0], [59.3, 200.0], [59.4, 200.0], [59.5, 200.0], [59.6, 200.0], [59.7, 200.0], [59.8, 200.0], [59.9, 200.0], [60.0, 200.0], [60.1, 200.0], [60.2, 200.0], [60.3, 201.0], [60.4, 201.0], [60.5, 201.0], [60.6, 201.0], [60.7, 201.0], [60.8, 201.0], [60.9, 201.0], [61.0, 201.0], [61.1, 201.0], [61.2, 201.0], [61.3, 202.0], [61.4, 202.0], [61.5, 202.0], [61.6, 202.0], [61.7, 202.0], [61.8, 202.0], [61.9, 202.0], [62.0, 202.0], [62.1, 202.0], [62.2, 202.0], [62.3, 202.0], [62.4, 202.0], [62.5, 202.0], [62.6, 203.0], [62.7, 203.0], [62.8, 203.0], [62.9, 203.0], [63.0, 203.0], [63.1, 203.0], [63.2, 203.0], [63.3, 203.0], [63.4, 203.0], [63.5, 203.0], [63.6, 203.0], [63.7, 203.0], [63.8, 203.0], [63.9, 203.0], [64.0, 204.0], [64.1, 204.0], [64.2, 204.0], [64.3, 204.0], [64.4, 204.0], [64.5, 204.0], [64.6, 204.0], [64.7, 204.0], [64.8, 204.0], [64.9, 205.0], [65.0, 205.0], [65.1, 205.0], [65.2, 205.0], [65.3, 205.0], [65.4, 205.0], [65.5, 205.0], [65.6, 205.0], [65.7, 205.0], [65.8, 206.0], [65.9, 206.0], [66.0, 206.0], [66.1, 206.0], [66.2, 206.0], [66.3, 206.0], [66.4, 206.0], [66.5, 206.0], [66.6, 206.0], [66.7, 206.0], [66.8, 206.0], [66.9, 207.0], [67.0, 207.0], [67.1, 207.0], [67.2, 207.0], [67.3, 207.0], [67.4, 207.0], [67.5, 207.0], [67.6, 207.0], [67.7, 207.0], [67.8, 207.0], [67.9, 207.0], [68.0, 207.0], [68.1, 207.0], [68.2, 207.0], [68.3, 208.0], [68.4, 208.0], [68.5, 208.0], [68.6, 208.0], [68.7, 208.0], [68.8, 208.0], [68.9, 208.0], [69.0, 208.0], [69.1, 208.0], [69.2, 209.0], [69.3, 209.0], [69.4, 209.0], [69.5, 209.0], [69.6, 209.0], [69.7, 210.0], [69.8, 210.0], [69.9, 210.0], [70.0, 210.0], [70.1, 210.0], [70.2, 210.0], [70.3, 210.0], [70.4, 211.0], [70.5, 211.0], [70.6, 211.0], [70.7, 211.0], [70.8, 211.0], [70.9, 211.0], [71.0, 211.0], [71.1, 211.0], [71.2, 211.0], [71.3, 212.0], [71.4, 212.0], [71.5, 212.0], [71.6, 212.0], [71.7, 212.0], [71.8, 212.0], [71.9, 212.0], [72.0, 212.0], [72.1, 212.0], [72.2, 212.0], [72.3, 213.0], [72.4, 213.0], [72.5, 213.0], [72.6, 213.0], [72.7, 213.0], [72.8, 213.0], [72.9, 213.0], [73.0, 214.0], [73.1, 214.0], [73.2, 214.0], [73.3, 214.0], [73.4, 214.0], [73.5, 214.0], [73.6, 214.0], [73.7, 214.0], [73.8, 214.0], [73.9, 214.0], [74.0, 214.0], [74.1, 214.0], [74.2, 214.0], [74.3, 214.0], [74.4, 214.0], [74.5, 215.0], [74.6, 215.0], [74.7, 215.0], [74.8, 215.0], [74.9, 215.0], [75.0, 215.0], [75.1, 215.0], [75.2, 215.0], [75.3, 215.0], [75.4, 215.0], [75.5, 215.0], [75.6, 216.0], [75.7, 216.0], [75.8, 216.0], [75.9, 216.0], [76.0, 216.0], [76.1, 216.0], [76.2, 217.0], [76.3, 217.0], [76.4, 217.0], [76.5, 217.0], [76.6, 217.0], [76.7, 217.0], [76.8, 217.0], [76.9, 217.0], [77.0, 217.0], [77.1, 218.0], [77.2, 218.0], [77.3, 218.0], [77.4, 218.0], [77.5, 218.0], [77.6, 218.0], [77.7, 218.0], [77.8, 218.0], [77.9, 219.0], [78.0, 219.0], [78.1, 219.0], [78.2, 219.0], [78.3, 219.0], [78.4, 219.0], [78.5, 219.0], [78.6, 219.0], [78.7, 220.0], [78.8, 220.0], [78.9, 220.0], [79.0, 220.0], [79.1, 220.0], [79.2, 220.0], [79.3, 220.0], [79.4, 220.0], [79.5, 220.0], [79.6, 221.0], [79.7, 221.0], [79.8, 221.0], [79.9, 221.0], [80.0, 221.0], [80.1, 221.0], [80.2, 221.0], [80.3, 221.0], [80.4, 221.0], [80.5, 222.0], [80.6, 222.0], [80.7, 222.0], [80.8, 222.0], [80.9, 222.0], [81.0, 222.0], [81.1, 222.0], [81.2, 223.0], [81.3, 223.0], [81.4, 223.0], [81.5, 223.0], [81.6, 223.0], [81.7, 223.0], [81.8, 223.0], [81.9, 223.0], [82.0, 224.0], [82.1, 224.0], [82.2, 224.0], [82.3, 224.0], [82.4, 225.0], [82.5, 225.0], [82.6, 225.0], [82.7, 225.0], [82.8, 225.0], [82.9, 226.0], [83.0, 226.0], [83.1, 226.0], [83.2, 226.0], [83.3, 226.0], [83.4, 226.0], [83.5, 226.0], [83.6, 227.0], [83.7, 227.0], [83.8, 227.0], [83.9, 227.0], [84.0, 227.0], [84.1, 228.0], [84.2, 228.0], [84.3, 228.0], [84.4, 228.0], [84.5, 229.0], [84.6, 229.0], [84.7, 230.0], [84.8, 230.0], [84.9, 230.0], [85.0, 231.0], [85.1, 231.0], [85.2, 231.0], [85.3, 231.0], [85.4, 232.0], [85.5, 232.0], [85.6, 232.0], [85.7, 232.0], [85.8, 233.0], [85.9, 233.0], [86.0, 233.0], [86.1, 233.0], [86.2, 233.0], [86.3, 233.0], [86.4, 234.0], [86.5, 234.0], [86.6, 234.0], [86.7, 234.0], [86.8, 235.0], [86.9, 235.0], [87.0, 235.0], [87.1, 235.0], [87.2, 236.0], [87.3, 236.0], [87.4, 236.0], [87.5, 236.0], [87.6, 237.0], [87.7, 237.0], [87.8, 238.0], [87.9, 238.0], [88.0, 238.0], [88.1, 239.0], [88.2, 239.0], [88.3, 239.0], [88.4, 239.0], [88.5, 240.0], [88.6, 240.0], [88.7, 241.0], [88.8, 242.0], [88.9, 242.0], [89.0, 242.0], [89.1, 242.0], [89.2, 242.0], [89.3, 243.0], [89.4, 243.0], [89.5, 243.0], [89.6, 244.0], [89.7, 244.0], [89.8, 244.0], [89.9, 245.0], [90.0, 245.0], [90.1, 246.0], [90.2, 246.0], [90.3, 246.0], [90.4, 246.0], [90.5, 247.0], [90.6, 247.0], [90.7, 247.0], [90.8, 248.0], [90.9, 248.0], [91.0, 249.0], [91.1, 249.0], [91.2, 250.0], [91.3, 250.0], [91.4, 251.0], [91.5, 251.0], [91.6, 252.0], [91.7, 253.0], [91.8, 254.0], [91.9, 254.0], [92.0, 255.0], [92.1, 256.0], [92.2, 257.0], [92.3, 258.0], [92.4, 258.0], [92.5, 259.0], [92.6, 259.0], [92.7, 260.0], [92.8, 262.0], [92.9, 263.0], [93.0, 263.0], [93.1, 265.0], [93.2, 266.0], [93.3, 266.0], [93.4, 268.0], [93.5, 268.0], [93.6, 268.0], [93.7, 269.0], [93.8, 269.0], [93.9, 270.0], [94.0, 272.0], [94.1, 273.0], [94.2, 274.0], [94.3, 275.0], [94.4, 276.0], [94.5, 277.0], [94.6, 278.0], [94.7, 279.0], [94.8, 280.0], [94.9, 282.0], [95.0, 283.0], [95.1, 284.0], [95.2, 285.0], [95.3, 286.0], [95.4, 287.0], [95.5, 287.0], [95.6, 288.0], [95.7, 289.0], [95.8, 292.0], [95.9, 292.0], [96.0, 295.0], [96.1, 295.0], [96.2, 298.0], [96.3, 301.0], [96.4, 301.0], [96.5, 305.0], [96.6, 306.0], [96.7, 308.0], [96.8, 309.0], [96.9, 316.0], [97.0, 322.0], [97.1, 328.0], [97.2, 332.0], [97.3, 334.0], [97.4, 339.0], [97.5, 340.0], [97.6, 344.0], [97.7, 357.0], [97.8, 363.0], [97.9, 372.0], [98.0, 380.0], [98.1, 388.0], [98.2, 396.0], [98.3, 397.0], [98.4, 398.0], [98.5, 401.0], [98.6, 415.0], [98.7, 423.0], [98.8, 444.0], [98.9, 462.0], [99.0, 630.0], [99.1, 715.0], [99.2, 737.0], [99.3, 809.0], [99.4, 815.0], [99.5, 1007.0], [99.6, 1104.0], [99.7, 1157.0], [99.8, 1198.0], [99.9, 1241.0]], "isOverall": false, "label": "HTTP请求", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 100.0, "title": "Response Time Percentiles"}},
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
        data: {"result": {"minY": 1.0, "minX": 0.0, "maxY": 1142.0, "series": [{"data": [[0.0, 47.0], [600.0, 2.0], [700.0, 4.0], [200.0, 755.0], [800.0, 4.0], [1000.0, 2.0], [1100.0, 5.0], [300.0, 44.0], [1200.0, 3.0], [1300.0, 1.0], [400.0, 10.0], [100.0, 1142.0], [500.0, 1.0]], "isOverall": false, "label": "HTTP请求", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 100, "maxX": 1300.0, "title": "Response Time Distribution"}},
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
        data: {"result": {"minY": 22.0, "minX": 0.0, "ticks": [[0, "Requests having \nresponse time <= 500ms"], [1, "Requests having \nresponse time > 500ms and <= 1,500ms"], [2, "Requests having \nresponse time > 1,500ms"], [3, "Requests in error"]], "maxY": 1998.0, "series": [{"data": [[0.0, 1998.0]], "color": "#9ACD32", "isOverall": false, "label": "Requests having \nresponse time <= 500ms", "isController": false}, {"data": [[1.0, 22.0]], "color": "yellow", "isOverall": false, "label": "Requests having \nresponse time > 500ms and <= 1,500ms", "isController": false}, {"data": [], "color": "orange", "isOverall": false, "label": "Requests having \nresponse time > 1,500ms", "isController": false}, {"data": [], "color": "#FF6347", "isOverall": false, "label": "Requests in error", "isController": false}], "supportsControllersDiscrimination": false, "maxX": 1.0, "title": "Synthetic Response Times Distribution"}},
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
        data: {"result": {"minY": 19.323267326732662, "minX": 1.79317152E12, "maxY": 19.323267326732662, "series": [{"data": [[1.79317152E12, 19.323267326732662]], "isOverall": false, "label": "线程组", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79317152E12, "title": "Active Threads Over Time"}},
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
        data: {"result": {"minY": 27.0, "minX": 1.0, "maxY": 212.68445747800575, "series": [{"data": [[8.0, 97.4], [2.0, 37.0], [9.0, 41.2], [10.0, 94.44444444444444], [11.0, 126.0], [12.0, 116.0], [3.0, 33.0], [13.0, 121.13636363636363], [14.0, 129.33333333333334], [15.0, 133.08333333333331], [16.0, 162.66666666666669], [4.0, 66.0], [1.0, 27.0], [17.0, 152.6818181818182], [18.0, 166.71249999999998], [19.0, 174.7777777777778], [20.0, 212.68445747800575], [5.0, 93.5], [6.0, 83.0], [7.0, 151.33333333333334]], "isOverall": false, "label": "HTTP请求", "isController": false}, {"data": [[19.323267326732662, 202.31039603960397]], "isOverall": false, "label": "HTTP请求-Aggregated", "isController": false}], "supportsControllersDiscrimination": true, "maxX": 20.0, "title": "Time VS Threads"}},
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
        data : {"result": {"minY": 15344.666666666666, "minX": 1.79317152E12, "maxY": 65394.333333333336, "series": [{"data": [[1.79317152E12, 65394.333333333336]], "isOverall": false, "label": "Bytes received per second", "isController": false}, {"data": [[1.79317152E12, 15344.666666666666]], "isOverall": false, "label": "Bytes sent per second", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79317152E12, "title": "Bytes Throughput Over Time"}},
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
        data: {"result": {"minY": 202.31039603960397, "minX": 1.79317152E12, "maxY": 202.31039603960397, "series": [{"data": [[1.79317152E12, 202.31039603960397]], "isOverall": false, "label": "HTTP请求", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79317152E12, "title": "Response Time Over Time"}},
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
        data: {"result": {"minY": 202.20792079207928, "minX": 1.79317152E12, "maxY": 202.20792079207928, "series": [{"data": [[1.79317152E12, 202.20792079207928]], "isOverall": false, "label": "HTTP请求", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79317152E12, "title": "Latencies Over Time"}},
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
        data: {"result": {"minY": 0.854950495049505, "minX": 1.79317152E12, "maxY": 0.854950495049505, "series": [{"data": [[1.79317152E12, 0.854950495049505]], "isOverall": false, "label": "HTTP请求", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79317152E12, "title": "Connect Time Over Time"}},
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
        data: {"result": {"minY": 14.0, "minX": 1.79317152E12, "maxY": 1319.0, "series": [{"data": [[1.79317152E12, 1319.0]], "isOverall": false, "label": "Max", "isController": false}, {"data": [[1.79317152E12, 14.0]], "isOverall": false, "label": "Min", "isController": false}, {"data": [[1.79317152E12, 245.0]], "isOverall": false, "label": "90th percentile", "isController": false}, {"data": [[1.79317152E12, 654.4899999999989]], "isOverall": false, "label": "99th percentile", "isController": false}, {"data": [[1.79317152E12, 192.0]], "isOverall": false, "label": "Median", "isController": false}, {"data": [[1.79317152E12, 282.9499999999998]], "isOverall": false, "label": "95th percentile", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79317152E12, "title": "Response Time Percentiles Over Time (successful requests only)"}},
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
    data: {"result": {"minY": 72.0, "minX": 23.0, "maxY": 431.0, "series": [{"data": [[41.0, 431.0], [51.0, 72.0], [82.0, 198.0], [86.0, 236.0], [85.0, 234.0], [95.0, 208.0], [93.0, 201.0], [23.0, 105.0], [98.0, 206.0], [101.0, 200.5], [103.0, 190.0], [100.0, 197.0], [105.0, 189.0], [104.0, 190.0], [108.0, 179.0], [109.0, 183.0], [111.0, 168.0], [113.0, 136.0]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 113.0, "title": "Response Time Vs Request"}},
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
    data: {"result": {"minY": 71.0, "minX": 23.0, "maxY": 431.0, "series": [{"data": [[41.0, 431.0], [51.0, 71.0], [82.0, 198.0], [86.0, 236.0], [85.0, 234.0], [95.0, 208.0], [93.0, 201.0], [23.0, 105.0], [98.0, 206.0], [101.0, 200.5], [103.0, 190.0], [100.0, 197.0], [105.0, 189.0], [104.0, 190.0], [108.0, 179.0], [109.0, 183.0], [111.0, 168.0], [113.0, 136.0]], "isOverall": false, "label": "Successes", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 1000, "maxX": 113.0, "title": "Latencies Vs Request"}},
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
        data: {"result": {"minY": 33.666666666666664, "minX": 1.79317152E12, "maxY": 33.666666666666664, "series": [{"data": [[1.79317152E12, 33.666666666666664]], "isOverall": false, "label": "hitsPerSecond", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79317152E12, "title": "Hits Per Second"}},
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
        data: {"result": {"minY": 33.666666666666664, "minX": 1.79317152E12, "maxY": 33.666666666666664, "series": [{"data": [[1.79317152E12, 33.666666666666664]], "isOverall": false, "label": "200", "isController": false}], "supportsControllersDiscrimination": false, "granularity": 60000, "maxX": 1.79317152E12, "title": "Codes Per Second"}},
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
        data: {"result": {"minY": 33.666666666666664, "minX": 1.79317152E12, "maxY": 33.666666666666664, "series": [{"data": [[1.79317152E12, 33.666666666666664]], "isOverall": false, "label": "HTTP请求-success", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79317152E12, "title": "Transactions Per Second"}},
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
        data: {"result": {"minY": 33.666666666666664, "minX": 1.79317152E12, "maxY": 33.666666666666664, "series": [{"data": [[1.79317152E12, 33.666666666666664]], "isOverall": false, "label": "Transaction-success", "isController": false}, {"data": [], "isOverall": false, "label": "Transaction-failure", "isController": false}], "supportsControllersDiscrimination": true, "granularity": 60000, "maxX": 1.79317152E12, "title": "Total Transactions Per Second"}},
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

