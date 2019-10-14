# HTTP模块剩余

## referer模块

`ngx_http_referer_module`提供防盗链功能，当某个网站通过url引用了自己的页面时，用户点击url，http请求会通过referer头部字段将当前的网站url带上，告知服务器本次请求的发起页面。`referer`模块提供`invalid_referer`变量来判断`referer`头部是否合法，默认不编译进nginx。`referer`模块只能防止通过浏览器的盗链行为，而不能防攻击者，因为该字段很容易被篡改。

- `valid_referers`：判断

```nginx
Syntax: valid_referers none | blocked | server_names | string ...;
Default: —
Context: server, location
```

![valid_referers使用]()

- `referer_hash_bucket_size`：每个元素的大小。

```nginx
Syntax: referer_hash_bucket_size size;
Default: referer_hash_bucket_size 64;
Context: server, location
```

- `referer_hash_max_size`：最大个数。

```nginx
Syntax: referer_hash_max_size size;
Default: referer_hash_max_size 2048;
Context: server, location
```

## secure_link

`ngx_http_secure_link_module`模块提供了新的防盗链功能。其核心是通过验证URL中的哈希值来防盗链。服务器生成加密后的安全连接返回给客户端，客户端通过安全连接访问，由nginx的遍历`secure_link`来判断是否验证通过。默认不编译进入nginx。其原理是：

- 哈希算法不可逆，客户端只能拿到经过hash算法的URL。
- 只有生成URL的服务器和nginx才能拿到URL原始字符串。
- 原始字符串的内容：
  - 资源的位置，防止攻击者拿到一个安全URL后访问任意资源。
  - 用户信息，包含IP地址，限制其他用户盗用安全URL。
  - 时间戳，让安全URL及时过期。
  - 密钥，只由服务端拥有，增加攻击者猜测原始字符串的难度。

`secure_link`提供两个变量：

- `secure_link`：判断是否是安全连接
- `secure_link_expires`：时间戳。

`secure_link`提供三个指令：

- `secure_link`

```
Syntax: secure_link expression;
Default: —
Context: http, server, location
```

- `secure_link_md5`：

```
Syntax: secure_link_md5 expression;
Default: —
Context: http, server, location
```

- `secure_link_secret`：

```
Syntax: secure_link_secret word;
Default: —
Context: location
```

变量值及过期时间的配置，可以对用户、时间戳进行区分：

```nginx
# secure_link参数根据URL中md5和expires参数生成
# aa.com/a.txt?md5=***&expires=***
secure_link $arg_md5,$arg_expires;
# md5值的生成方式，secret是密钥值
secure_link_md5 "$secure_link_expires$uri$remote_addr secret";
# md5值可以通过指令生成：
# echo -n '时间戳URL客户端IP secrte'| openssl md5 -binary | openssl base64 | tr +/ - | tr -d =
# 参数secure_link 为空，不通过，为0则过期，为1则通过。
```

仅对URL进行哈希的简单方法，只能对用户访问的资源URI进行区分：

```nginx
# URL被分为了三部分：/prefix/hash/link link为原连接
# hash值通过对`link密钥`求md5
# 通过secure_link_secret 配置密钥
	location /p/ {# p为前缀prefix
    		# md5值可以通过命令：
			# echo -n 'linksecret' | openssl md5 –hex
    		secure_link_secret mysecret2;

    		if ($secure_link = "") {
        		return 403;
    		}
			# 进行重定向
    		rewrite ^ /secure/$secure_link;
	}

	location /secure/ {
		alias html/;
    	internal;
	}
```

## map模块

`ngx_http_map_module`模块可以通过多个变量组合形成的新变量值进行逻辑判断。默认编译到Nginx中。`map`基于已经存在的变量，采用类似`switch{case :...，default:...}`的语法创建新的变量。

- `map`：`variable`为新变量。

```nginx
Syntax: map string $variable { ... }
Default: —
Context: http
```

- `map_hash_bucket_size`：通过hash表加速，单个元素大小。

```nginx
Syntax: map_hash_bucket_size size;
Default: map_hash_bucket_size 32|64|128;
Context: http
```

- `map_hash_max_size`

```nginx
Syntax: map_hash_max_size size;
Default: map_hash_max_size 2048;
Context: http
```

![map模块的规则]()

```nginx
map $http_host $name {
hostnames;
default 0;
~map\.tao\w+\.org.cn 1;# 'Host: map.tao123.org.cn
*.taohui.org.cn 2; # 'Host: map.taohui.org.cn'
map.taohui.tech 3;# 'Host: map.taohui.tech'
map.taohui.* 4;# 'Host: map.taohui.pub'
}
map $http_user_agent $mobile {
default 0;
"~Opera Mini" 1;
}
# 匹配规则：
# 字符串严格匹配
# 前缀泛域名
# 后缀泛域名
# 正则表达式
```

## split_clients模块

`ngx_http_split_clients`模块对已有的变量进行MurmurHash2 ，然后计算百分比，通过百分比来创建新的变量，来提供AB测试。默认编译进入nginx。

![split_clients模块]()

- `split_clients`：创建一个新变量

```nginx
Syntax: split_clients string $variable { ... }
Default: —
Context: http
```

示范

```nginx
split_clients "${http_testcli}" $variant {
         0.51%          .one;
         20.0%          .two;
         50.5%          .three;
         #40%           .four;
         *              "";
}

server {
        server_name split_clients.taohui.tech;
        error_log  logs/error.log  debug;
        default_type text/plain;
        location /{# 可以通过if指令来执行反向代理
                return 200 'ABtestfile$variant\n';
        }
}
```

## geo模块

`ngx_http_geo_module`模块基于IP地址来创建新的变量，默认编译进入nginx。

- `geo`：基于IP地址或子网掩码创建新的变量，如果不使用$address，默认使用remote_addr

```
Syntax: geo [$address] $variable { ... }
Default: —
Context: http
```

匹配规则：最长匹配，子网掩码越大，优先匹配。

![geo匹配规则]()

```
geo $country {
default ZZ;
#include conf/geo.conf;
proxy 116.62.160.193;
127.0.0.0/24 US;
127.0.0.1/32 RU;
10.1.0.0/16 RU;
192.168.1.0/24 UK;
}
```

## geoip模块

`ngx_http_geoip_module`提供根据IP地址获取地理位置的功能。该模块需要[MaxMind](dev.maxmind.com/geoip/geoip2/geolite2)的geoip的[c开发库](https://dev.maxmind.com/geoip/
legacy/downloadable/ )，编译时需要使用`--withhttp_geoip_module`参数。geoip还需要下载MaxMind中的二进制地址库。

国家信息：

- `geoip_country`：配置二进制地址库位置，需要绝对路径。

```nginx
Syntax: geoip_country file;
Default: —
Context: http
```

- `geoip_proxy`：提供可信地址。

```nginx
Syntax: geoip_proxy address | CIDR;
Default: —
Context: http
```

提供的变量：

- `geoip_country_code`：两个字母的国家代码，如CN
- `geoip_country_code3`：三个字母的国家代码，如CHN
- `geoip_country_name`：国家全称，如China

城市信息：

- `geoip_city`：指定城市文件位置(全集)。

```nginx
Syntax: geoip_city file;
Default: —
Context: http
```

提供的变量：

![geoip_city提供的变量]()

实例：

```nginx
geo $country {
    default        ZZ;
    #include        conf/geo.conf;
    proxy          116.62.160.193;

    127.0.0.0/24   US;
    127.0.0.1/32   RU;
    10.1.0.0/16    RU;
    192.168.1.0/24 UK;
}

server {
	server_name geo.taohui.tech;
	location /{
                return 200 '$country\n';
        }
}

geoip_country         /usr/local/share/GeoIP/GeoIP.dat;
geoip_city            /usr/local/share/GeoIP/GeoLiteCity.dat;
geoip_proxy           116.62.160.193/32;
geoip_proxy_recursive on;

server {
	server_name geoip.taohui.tech;
	error_log logs/myerror.log info;
	keepalive_requests 2;
	keepalive_timeout 75s 20;
	location /{
		return 200 'country:$geoip_country_code,$geoip_country_code3,$geoip_country_name
country from city:$geoip_city_country_code,$geoip_city_country_code3,$geoip_city_country_name
city:$geoip_area_code,$geoip_city_continent_code,$geoip_dma_code
$geoip_latitude,$geoip_longitude,$geoip_region,$geoip_region_name,$geoip_city,$geoip_postal_code
';
	}
```

通过代理网站`www.guobanjia.com`验证

## keepalive

通过多个HTTP请求通过复用TCP连接，以达到：

- 减少握手次数
- 通过减少并发连接数降低服务器资源消耗。
- 降低TCP拥塞控制的影响。

在HTTP协议中，有两个头部字段会有影响：

- `Connection`：为`close`处理完请求后立即关闭连接，`keepalive`则继续复用。
- `Keep-Alive`：其值为`timeout=n`，要求客户端至少保留n秒。

nginx中相关的指令有：

- `keepalive_disable`：对某些浏览器关闭`keepalive`功能。

```nginx
Syntax: keepalive_disable none | browser ...;
Default: keepalive_disable msie6;
Context: http, server, location
```

- `keepalive_requests`：一个TCP连接上最多执行多少个http请求。

```nginx
Syntax: keepalive_requests number;
Default: keepalive_requests 100;
Context: http, server, location
```

- `keepalive_timeout`：第一个timeout，下一个请求最大的间隔时间，header_timeout为返回的头部字段中`Keep-Alive`字段。

```nginx
Syntax: keepalive_timeout timeout [header_timeout];
Default: keepalive_timeout 75s;
Context: http, server, location
```
