---
authors: [dmerej]
slug: "using-let-s-encrypt-on-debian-8"
date: "2016-07-10T11:44:10+02:00"
description: ""
draft: true
title: "Using Let's Encrypt on Debian 8"
tags: ["misc"]
---

Short guide for installing Let's Encrypt on Debian 8, and get an 'A'
on SSL Labs.

<!--more-->

# Installing and using certbot

* Enable backports

* Install certbot

```console
# apt-get install certbot -t jessie-backports
```
(You need `-t` since by default packages from `backports`
have lower priority)

* Remove cron stuff installed by default:

```console
# rm /etc/cron.d/certbot
```

* Run the configuration dialog, using staging environment

```console
# certbot certonly --staging
```

We asked for the `webroot` path, enter `/srv/www` for instance
(Make sure to have a big window!
See [the bug on github](https://github.com/certbot/certbot/issues/2787)


* We now have a `.pem` file in
`/etc/letsencrypt/live/dmerej.info/fullchain.pem`

* Configure nginx:

```nginx
http {
  listen 443 ssl;
  ssl_certificate      /etc/letsencrypt/live/dmerej.info/fullchain.pem;
  ssl_certificate_key  /etc/letsencrypt/live/dmerej.info/privkey.pem;
}
```

* Note: make sure to use `fullchain.pem` and not just `cert.pem`, otherwise
  you'll get an error saying the certificate chain is incomplete

* Check syntax OK and restart nginx

```console
# nginx -t
# nginx -s reload
```

* Try to open `https://dmerej.info` in a web browser: certificate is
  invalid and belongs to "Fake LE Intermediate X1"


# Using real acme API

* Re-run `certbot certonly` without the `--staging` option

* Choose "Renew & Replace the cert"

* Restart `nginx` (just running `nginx -s reload` won't suffice)

* Allow incoming connections to `443` port


# Checks

Use [sslab](https://www.ssllabs.com/ssltest/) to check: 3 problems

* Weak Diffie-Hellman (DH) key exchange parameters
  * Not sure what this is about, but the doc is clear enough:
    [Guide to Deploying Diffie-Hellman for TLS](https://weakdh.org/sysadmin.html)

* No support for Forward Secrecy
  * Ditto: [nginx and forward secrecy](
    https://blog.qualys.com/ssllabs/2013/08/05/configuring-apache-nginx-and-openssl-for-forward-secrecy)
  * Important: it means that if someone steals your private key, he can't
    decrypt previous conversations

* Certificate chain is incomplete
  * Use `fullchain.pem` instead of just `cert.pem`


# More stuff

* Rebuild the blog to use `httpS://dmerej.info/blog` as base URL.
  Otherwise when browsing 'https://dmerej.info/blog', browser will
  refuse to download stuff like `css` that are still served in http ...


* Configure nginx to redirect http to https:


```nginx
server {

  server_name dmerej.info;

  # Redirect http traffic to https
  if ($scheme = 'http') {
          return 301 https://$server_name$request_uri;
  }

}
```

* Add a note in personal calendar to renew the certificate in 3 months
