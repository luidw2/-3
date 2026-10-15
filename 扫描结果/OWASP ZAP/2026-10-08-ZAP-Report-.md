# ZAP by Checkmarx Scanning Report

ZAP by [Checkmarx](https://checkmarx.com/).


## 警报汇总

| 风险水平 | 警报数量 |
| --- | --- |
| 高 | 0 |
| 中 | 2 |
| 低 | 1 |
| 信息提示 | 2 |




## Insights

| Level | Reason | Site | Description | Statistic |
| --- | --- | --- | --- | --- |
| Low | Warning |  | ZAP errors logged - see the zap.log file for details | 2    |
| Low | Warning |  | ZAP warnings logged - see the zap.log file for details | 5    |
| Info | Informational | http://192.168.133.1:5173 | Percentage of responses with status code 2xx | 100 % |
| Info | Informational | http://192.168.133.1:5173 | Percentage of endpoints with content type image/svg+xml | 2 % |
| Info | Informational | http://192.168.133.1:5173 | Percentage of endpoints with content type text/html | 4 % |
| Info | Informational | http://192.168.133.1:5173 | Percentage of endpoints with content type text/javascript | 91 % |
| Info | Informational | http://192.168.133.1:5173 | Percentage of endpoints with method GET | 100 % |
| Info | Informational | http://192.168.133.1:5173 | Count of total endpoints | 69    |
| Info | Informational | http://192.168.133.1:5173 | Percentage of slow responses | 75 % |
| Info | Informational | https://firefox-settings-attachments.cdn.mozilla.net | Percentage of endpoints with content type application/octet-stream | 100 % |
| Info | Informational | https://firefox-settings-attachments.cdn.mozilla.net | Percentage of endpoints with method GET | 100 % |
| Info | Informational | https://firefox-settings-attachments.cdn.mozilla.net | Count of total endpoints | 1    |
| Info | Informational | https://firefox.settings.services.mozilla.com | Percentage of endpoints with content type application/json | 100 % |
| Info | Informational | https://firefox.settings.services.mozilla.com | Percentage of endpoints with method GET | 100 % |
| Info | Informational | https://firefox.settings.services.mozilla.com | Count of total endpoints | 1    |




## 警报

| 名称 | 风险水平 | 实例数 |
| --- | --- | --- |
| Content Security Policy (CSP) Header Not Set | 中 | 3 |
| Missing Anti-clickjacking Header | 中 | 3 |
| X-Content-Type-Options Header Missing | 低 | Systemic |
| Information Disclosure - Suspicious Comments | 信息提示 | 1 |
| 现代 Web 应用程序 | 信息提示 | 3 |




## 警报详情



### [ Content Security Policy (CSP) Header Not Set ](https://www.zaproxy.org/docs/alerts/10038/)



##### 中 (高)

### 说明

Content Security Policy (CSP) is an added layer of security that helps to detect and mitigate certain types of attacks, including Cross Site Scripting (XSS) and data injection attacks. These attacks are used for everything from data theft to site defacement or distribution of malware. CSP provides a set of standard HTTP headers that allow website owners to declare approved sources of content that browsers should be allowed to load on that page — covered types are JavaScript, CSS, HTML frames, fonts, images and embeddable objects such as Java applets, ActiveX, audio and video files.

* URL: http://192.168.133.1:5173/
  * 节点名称: `http://192.168.133.1:5173/`
  * 方法: `GET`
  * 参数: ``
  * 攻击: ``
  * 证据: ``
  * 其他信息: ``
* URL: http://192.168.133.1:5173/robots.txt
  * 节点名称: `http://192.168.133.1:5173/robots.txt`
  * 方法: `GET`
  * 参数: ``
  * 攻击: ``
  * 证据: ``
  * 其他信息: ``
* URL: http://192.168.133.1:5173/sitemap.xml
  * 节点名称: `http://192.168.133.1:5173/sitemap.xml`
  * 方法: `GET`
  * 参数: ``
  * 攻击: ``
  * 证据: ``
  * 其他信息: ``


实例: 3

### 解决方案

Ensure that your web server, application server, load balancer, etc. is configured to set the Content-Security-Policy header.

### 参考


* [ https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP ](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP)
* [ https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html ](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)
* [ https://www.w3.org/TR/CSP/ ](https://www.w3.org/TR/CSP/)
* [ https://w3c.github.io/webappsec-csp/ ](https://w3c.github.io/webappsec-csp/)
* [ https://web.dev/articles/csp ](https://web.dev/articles/csp)
* [ https://caniuse.com/#feat=contentsecuritypolicy ](https://caniuse.com/#feat=contentsecuritypolicy)
* [ https://content-security-policy.com/ ](https://content-security-policy.com/)


#### CWE Id: [ 693 ](https://cwe.mitre.org/data/definitions/693.html)


#### WASC Id: 15

#### 源 ID: 3

### [ Missing Anti-clickjacking Header ](https://www.zaproxy.org/docs/alerts/10020/)



##### 中 (中)

### 说明

The response does not protect against 'ClickJacking' attacks. It should include either Content-Security-Policy with 'frame-ancestors' directive or X-Frame-Options.

* URL: http://192.168.133.1:5173/
  * 节点名称: `http://192.168.133.1:5173/`
  * 方法: `GET`
  * 参数: `x-frame-options`
  * 攻击: ``
  * 证据: ``
  * 其他信息: ``
* URL: http://192.168.133.1:5173/robots.txt
  * 节点名称: `http://192.168.133.1:5173/robots.txt`
  * 方法: `GET`
  * 参数: `x-frame-options`
  * 攻击: ``
  * 证据: ``
  * 其他信息: ``
* URL: http://192.168.133.1:5173/sitemap.xml
  * 节点名称: `http://192.168.133.1:5173/sitemap.xml`
  * 方法: `GET`
  * 参数: `x-frame-options`
  * 攻击: ``
  * 证据: ``
  * 其他信息: ``


实例: 3

### 解决方案

Modern Web browsers support the Content-Security-Policy and X-Frame-Options HTTP headers. Ensure one of them is set on all web pages returned by your site/app.
If you expect the page to be framed only by pages on your server (e.g. it's part of a FRAMESET) then you'll want to use SAMEORIGIN, otherwise if you never expect the page to be framed, you should use DENY. Alternatively consider implementing Content Security Policy's "frame-ancestors" directive.

### 参考


* [ https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Frame-Options ](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/X-Frame-Options)


#### CWE Id: [ 1021 ](https://cwe.mitre.org/data/definitions/1021.html)


#### WASC Id: 15

#### 源 ID: 3

### [ X-Content-Type-Options Header Missing ](https://www.zaproxy.org/docs/alerts/10021/)



##### 低 (中)

### 说明

The Anti-MIME-Sniffing header X-Content-Type-Options was not set to 'nosniff'. This allows older versions of Internet Explorer and Chrome to perform MIME-sniffing on the response body, potentially causing the response body to be interpreted and displayed as a content type other than the declared content type. Current (early 2014) and legacy versions of Firefox will use the declared content type (if one is set), rather than performing MIME-sniffing.

* URL: http://192.168.133.1:5173/
  * 节点名称: `http://192.168.133.1:5173/`
  * 方法: `GET`
  * 参数: `x-content-type-options`
  * 攻击: ``
  * 证据: ``
  * 其他信息: `This issue still applies to error type pages (401, 403, 500, etc.) as those pages are often still affected by injection issues, in which case there is still concern for browsers sniffing pages away from their actual content type.
At "High" threshold this scan rule will not alert on client or server error responses.`
* URL: http://192.168.133.1:5173/robots.txt
  * 节点名称: `http://192.168.133.1:5173/robots.txt`
  * 方法: `GET`
  * 参数: `x-content-type-options`
  * 攻击: ``
  * 证据: ``
  * 其他信息: `This issue still applies to error type pages (401, 403, 500, etc.) as those pages are often still affected by injection issues, in which case there is still concern for browsers sniffing pages away from their actual content type.
At "High" threshold this scan rule will not alert on client or server error responses.`
* URL: http://192.168.133.1:5173/sitemap.xml
  * 节点名称: `http://192.168.133.1:5173/sitemap.xml`
  * 方法: `GET`
  * 参数: `x-content-type-options`
  * 攻击: ``
  * 证据: ``
  * 其他信息: `This issue still applies to error type pages (401, 403, 500, etc.) as those pages are often still affected by injection issues, in which case there is still concern for browsers sniffing pages away from their actual content type.
At "High" threshold this scan rule will not alert on client or server error responses.`
* URL: http://192.168.133.1:5173/src/main.js
  * 节点名称: `http://192.168.133.1:5173/src/main.js`
  * 方法: `GET`
  * 参数: `x-content-type-options`
  * 攻击: ``
  * 证据: ``
  * 其他信息: `This issue still applies to error type pages (401, 403, 500, etc.) as those pages are often still affected by injection issues, in which case there is still concern for browsers sniffing pages away from their actual content type.
At "High" threshold this scan rule will not alert on client or server error responses.`
* URL: http://192.168.133.1:5173/vite.svg
  * 节点名称: `http://192.168.133.1:5173/vite.svg`
  * 方法: `GET`
  * 参数: `x-content-type-options`
  * 攻击: ``
  * 证据: ``
  * 其他信息: `This issue still applies to error type pages (401, 403, 500, etc.) as those pages are often still affected by injection issues, in which case there is still concern for browsers sniffing pages away from their actual content type.
At "High" threshold this scan rule will not alert on client or server error responses.`

实例: Systemic


### 解决方案

Ensure that the application/web server sets the Content-Type header appropriately, and that it sets the X-Content-Type-Options header to 'nosniff' for all web pages.
If possible, ensure that the end user uses a standards-compliant and modern web browser that does not perform MIME-sniffing at all, or that can be directed by the web application/web server to not perform MIME-sniffing.

### 参考


* [ https://learn.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/compatibility/gg622941(v=vs.85) ](https://learn.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/compatibility/gg622941(v=vs.85))
* [ https://owasp.org/www-community/Security_Headers ](https://owasp.org/www-community/Security_Headers)


#### CWE Id: [ 693 ](https://cwe.mitre.org/data/definitions/693.html)


#### WASC Id: 15

#### 源 ID: 3

### [ Information Disclosure - Suspicious Comments ](https://www.zaproxy.org/docs/alerts/10027/)



##### 信息提示 (低)

### 说明

The response appears to contain suspicious comments which may help an attacker.

* URL: http://192.168.133.1:5173/src/main.js
  * 节点名称: `http://192.168.133.1:5173/src/main.js`
  * 方法: `GET`
  * 参数: ``
  * 攻击: ``
  * 证据: `xxx`
  * 其他信息: `The following pattern was used: \bXXX\b and was detected in likely comment: "// —— UI 组件库 ant-design-vue：全量注册，页面里可直接使用 a-xxx 组件 ——", see evidence field for the suspicious comment/snippet.`


实例: 1

### 解决方案

Remove all comments that return information that may help an attacker and fix any underlying problems they refer to.

### 参考



#### CWE Id: [ 615 ](https://cwe.mitre.org/data/definitions/615.html)


#### WASC Id: 13

#### 源 ID: 3

### [ 现代 Web 应用程序 ](https://www.zaproxy.org/docs/alerts/10109/)



##### 信息提示 (中)

### 说明

The application appears to be a modern web application. If you need to explore it automatically then the Ajax Spider may well be more effective than the standard one.

* URL: http://192.168.133.1:5173/
  * 节点名称: `http://192.168.133.1:5173/`
  * 方法: `GET`
  * 参数: ``
  * 攻击: ``
  * 证据: `<script type="module" src="/@vite/client"></script>`
  * 其他信息: `No links have been found while there are scripts, which is an indication that this is a modern web application.`
* URL: http://192.168.133.1:5173/robots.txt
  * 节点名称: `http://192.168.133.1:5173/robots.txt`
  * 方法: `GET`
  * 参数: ``
  * 攻击: ``
  * 证据: `<script type="module" src="/@vite/client"></script>`
  * 其他信息: `No links have been found while there are scripts, which is an indication that this is a modern web application.`
* URL: http://192.168.133.1:5173/sitemap.xml
  * 节点名称: `http://192.168.133.1:5173/sitemap.xml`
  * 方法: `GET`
  * 参数: ``
  * 攻击: ``
  * 证据: `<script type="module" src="/@vite/client"></script>`
  * 其他信息: `No links have been found while there are scripts, which is an indication that this is a modern web application.`


实例: 3

### 解决方案

This is an informational alert and so no changes are required.

### 参考




#### 源 ID: 3


