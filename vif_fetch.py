
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VIF VPN 1.1.12
REGISTER -> MENU -> NODES -> ALL TROJAN + VLESS

Dependencies:
    pip install requests pycryptodome

Run:
    python vif_fetch.py

Termux output:
    Download/vif_out/

GitHub Actions:
    VIF_DOWNLOAD_DIR=output
"""

import os
import base64
import gzip
import json
import random
import string
import sys
import time
import uuid

from pathlib import Path
from urllib.parse import quote

import requests
import urllib3

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

# ============================================================
# SETTINGS
# ============================================================

PKG = "com.vifvpn.proxy.shield"
VER = "1.1.12"

COUNTRY = "fast"
CITY = ""

DEV_ID = ""
TIMEOUT = 20

if os.environ.get("VIF_DOWNLOAD_DIR"):
    DOWNLOAD_DIR = Path(os.environ["VIF_DOWNLOAD_DIR"])
else:
    DOWNLOAD_DIR = Path.home() / "storage" / "downloads"

    if not DOWNLOAD_DIR.exists():
        DOWNLOAD_DIR = Path("/storage/emulated/0/Download")

OUT_DIR = DOWNLOAD_DIR / "vif_out"
CONFIG_DIR = OUT_DIR / "xray_configs"

HOSTS = [
    "45.192.11.26",
    "45.192.11.47",
    "45.192.11.49",
    "game.packetforgewebs.com",
]

ROUTES = {
    "REGISTER": "tqofj/kyn/",
    "REFRESH": "jorx/",
    "USER": "ijfcw/",
    "NODES": "wmt/",
    "DOMAINS": "kugcr/tejd/jpkvq/",
    "CHECK": "kou/",
    "MENU": "nwjl/kfzbr/jdghwe/",
}

# ============================================================
# EMBEDDED BACKEND PROTOCOL
# ============================================================

PROTOCOL = {
    "fields": {
        "app": "wnkay",
        "bucket_id": "lois",
        "bucket_type": "jlnxvh",
        "channel": "jlce",
        "cities": "irwk",
        "city_name": "vuxrh",
        "client_ip": "qspev",
        "code": "lnvkqj",
        "comment": "lrkh",
        "config": "doxu",
        "count": "lfjq",
        "country_code": "vzofai",
        "country_name": "mzgf",
        "cover": "qucjsr",
        "create_time": "kvquo",
        "data": "rbegzl",
        "default": "ifzk",
        "dev_id": "xutql",
        "dev_name": "wsqpg",
        "email": "djsalx",
        "encrypt": "vlyf",
        "expire_ts": "vqdp",
        "flow_type": "ievr",
        "free_bucket_id": "oqzfi",
        "google_tk": "gxzh",
        "has_pay": "pwez",
        "info_b": "nmlkcg",
        "info_type": "nvai",
        "ip": "drzgie",
        "ip_v6": "lrqa",
        "is_in_intro_offer_period": "cdhrmn",
        "is_trial_period": "cyzls",
        "last_login": "mwcnt",
        "lat": "drtpv",
        "location": "uhrcd",
        "login_info": "fsgib",
        "login_type": "inpsm",
        "lon": "tkrlgx",
        "method": "zfwrjg",
        "micro_list": "uyhjz",
        "msg": "yptzcr",
        "name": "veudt",
        "network": "etvcl",
        "nickname": "tlvsp",
        "order_no": "vudl",
        "original_transaction_id": "fitech",
        "os": "rchpnx",
        "password": "cfgeao",
        "pay_status": "xisdm",
        "pm_id": "zvtys",
        "product_id": "dlkwi",
        "receipt": "lefr",
        "region": "yuqcsm",
        "seq": "ubmayd",
        "server": "swcp",
        "special": "mkjwfh",
        "ss_type": "pved",
        "status": "qaywkp",
        "tk": "urdl",
        "token": "cgobq",
        "total": "oytmk",
        "transaction_id": "wcky",
        "type": "nzrfd",
        "typology": "simng",
        "uid": "qlojh",
        "user_agent": "bvrm",
        "user_country": "toyheb",
        "username": "itvb",
        "vip": "ulkow",
        "vip_bucket_id": "brgztn",
        "vip_expire_ts": "vplh",
    },

    "headers": {
        "BFA": "DEV",
        "CMN": "UCT",
        "QKL": "VER",
        "RXQ": "PT",
        "SVQF": "DNM",
        "YFAV": "PKG",
        "ZPJE": "TK",
    },

    "codes": {
        "10002": 39860,
        "10010": 94318,
        "10011": 25480,
        "10012": 88880,
        "10013": 11714,
        "10015": 89999,
        "10016": 51210,
        "10017": 95753,
        "10019": 91012,
        "10022": 92252,
        "10023": 43460,
        "10025": 76637,
        "10026": 17411,
        "10027": 28719,
        "10029": 89991,
        "10030": 35747,
        "10100": 45203,
        "10101": 76995,
        "10102": 17382,
        "10103": 60073,
        "10104": 13137,
        "10402": 47024,
        "10404": 15130,
        "10500": 58971,
        "10501": 79187,
        "200": 12852,
    },

    "requestKey": "TgWoRq65rKu8XlBHJQ9n3E==",
    "responseKey": "z28ezAPWiZ9yXxNGEkaOch==",
}


# ============================================================
# AES
# ============================================================

def aes_ecb_encrypt(key, data):
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(pad(data, AES.block_size))


def aes_ecb_decrypt(key, data):
    cipher = AES.new(key, AES.MODE_ECB)
    return unpad(
        cipher.decrypt(data),
        AES.block_size
    )


def rand_az(n):
    return "".join(
        random.choice(string.ascii_lowercase)
        for _ in range(n)
    )


# ============================================================
# PROTOCOL
# ============================================================

class Protocol:

    def __init__(self, raw):

        self.raw = raw

        self.fields = raw["fields"]
        self.rev_fields = {
            v: k for k, v in self.fields.items()
        }

        self.headers_map = raw["headers"]
        self.inv_headers = {
            v: k for k, v in self.headers_map.items()
        }

        self.codes = {
            int(k): v
            for k, v in raw["codes"].items()
        }

        self.codes_inv = {
            v: int(k)
            for k, v in raw["codes"].items()
        }

        self.request_key = base64.b64decode(
            raw["requestKey"]
        )

        self.response_key = base64.b64decode(
            raw["responseKey"]
        )

        self.encrypt_field = self.fields["encrypt"]

        if len(self.request_key) not in (16, 24, 32):
            raise ValueError("Invalid AES request key")

        if len(self.response_key) not in (16, 24, 32):
            raise ValueError("Invalid AES response key")

    def map_fields(self, obj):

        if isinstance(obj, dict):
            return {
                self.fields.get(k, k): self.map_fields(v)
                for k, v in obj.items()
            }

        if isinstance(obj, list):
            return [
                self.map_fields(x)
                for x in obj
            ]

        return obj

    def unmap_fields(self, obj):

        if isinstance(obj, dict):
            return {
                self.rev_fields.get(k, k): self.unmap_fields(v)
                for k, v in obj.items()
            }

        if isinstance(obj, list):
            return [
                self.unmap_fields(x)
                for x in obj
            ]

        return obj

    def encrypt_body(self, body):

        plain = json.dumps(
            self.map_fields(body),
            separators=(",", ":"),
            ensure_ascii=False
        )

        b64 = base64.b64encode(
            plain.encode("utf-8")
        ).decode("ascii")

        if len(b64) >= 18:
            first9 = b64[:9]
            last9 = b64[-9:]
            mid = b64[9:-9]
            scrambled = last9 + mid + first9
        else:
            scrambled = b64

        payload = (
            rand_az(2) +
            scrambled[::-1] +
            rand_az(9)
        ).encode("utf-8")

        encrypted = aes_ecb_encrypt(
            self.request_key,
            payload
        )

        b1 = base64.b64encode(
            encrypted
        ).decode("ascii")

        b2 = base64.b64encode(
            b1.encode("ascii")
        ).decode("ascii")

        return json.dumps(
            {self.encrypt_field: b2},
            separators=(",", ":")
        )

    def decrypt_response(self, text):

        s = "".join(
            chr(ord(c) + 4)
            for c in text.strip()
        )[::-1]

        if len(s) <= 9:
            raise ValueError("Truncated response")

        s = s[1:len(s) - 8]

        mid = base64.b64decode(s).decode("utf-8")

        mid = "".join(
            c.upper() if "a" <= c <= "z"
            else c.lower() if "A" <= c <= "Z"
            else c
            for c in mid
        )

        encrypted = base64.b64decode(mid)

        plain = aes_ecb_decrypt(
            self.response_key,
            encrypted
        )

        try:
            plain = gzip.decompress(plain)
        except Exception:
            pass

        decoded = json.loads(
            plain.decode("utf-8")
        )

        return self.unmap_fields(decoded)

    def real_code(self, code):

        if code is None:
            return None

        return self.codes_inv.get(code, code)


# ============================================================
# HEADERS
# ============================================================

def build_headers(proto, dev_id, token=""):

    logical = {
        "PT": "ANDROID",
        "PKG": PKG,
        "VER": VER,
        "DEV": dev_id,
        "TK": token or "",
        "UCT": str(int(time.time() * 1000)),
        "DNM": "Pixel6",
    }

    headers = {
        "Content-Type": "application/json; charset=utf-8",
        "Accept": "application/json",
        "User-Agent": "okhttp/4.12.0",
    }

    for name, value in logical.items():
        wire_name = proto.inv_headers.get(name, name)
        headers[wire_name] = value

    return headers


# ============================================================
# API
# ============================================================

def api_post(host, route, body, proto, dev_id, token=""):

    url = f"https://{host}/apt/{ROUTES[route]}"

    encrypted_body = proto.encrypt_body(body)

    response = requests.post(
        url,
        data=encrypted_body.encode("utf-8"),
        headers=build_headers(proto, dev_id, token),
        timeout=TIMEOUT,
        verify=False
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"HTTP {response.status_code}: "
            f"{response.text[:200]}"
        )

    return proto.decrypt_response(response.text)


# ============================================================
# HOST DETECTION
# ============================================================

def pick_host(proto, dev_id):

    for host in HOSTS:

        try:

            data = api_post(
                host,
                "CHECK",
                {},
                proto,
                dev_id
            )

            code = proto.real_code(
                data.get("code")
            )

            if code == 200:
                print(f"[+] HOST: {host}")
                return host

            print(f"[!] {host}: code={code}")

        except Exception as error:
            print(f"[!] {host}: {error}")

    raise RuntimeError("Не найден доступный API host")


# ============================================================
# SAVE FUNCTIONS
# ============================================================

def save_json(path, data):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    path.write_text(
        json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ) + "\n",
        encoding="utf-8"
    )


def parse_config(config):

    if isinstance(config, dict):
        return config

    if isinstance(config, str):
        try:
            return json.loads(config)
        except json.JSONDecodeError:
            return None

    return None


# ============================================================
# URI HELPERS
# ============================================================

def add_param(params, name, value):

    if value is None or value == "":
        return

    if isinstance(value, bool):
        value = "1" if value else "0"

    elif isinstance(value, list):
        value = ",".join(str(x) for x in value)

    params.append(
        f"{name}={quote(str(value), safe='')}"
    )


def make_remark(remark, index, total):

    if total > 1:
        return f"{remark}-S{index}"

    return remark


def add_transport_params(params, stream):

    network = stream.get("network", "tcp")

    add_param(params, "type", network)

    if network == "httpupgrade":

        hu = stream.get("httpupgradeSettings") or {}

        add_param(params, "path", hu.get("path"))
        add_param(params, "host", hu.get("host"))

    elif network == "ws":

        ws = stream.get("wsSettings") or {}

        add_param(params, "path", ws.get("path"))

        ws_host = (
            ws.get("headers") or {}
        ).get("Host")

        add_param(params, "host", ws_host)

    elif network == "grpc":

        grpc = stream.get("grpcSettings") or {}

        add_param(
            params,
            "serviceName",
            grpc.get("serviceName")
        )

        add_param(
            params,
            "authority",
            grpc.get("authority")
        )

        if "multiMode" in grpc:
            mode = "multi" if grpc["multiMode"] else "gun"
            add_param(params, "mode", mode)

    elif network == "tcp":

        tcp = stream.get("tcpSettings") or {}
        header = tcp.get("header") or {}

        add_param(
            params,
            "headerType",
            header.get("type")
        )

        request = header.get("request") or {}
        headers = request.get("headers") or {}

        add_param(
            params,
            "host",
            headers.get("Host")
        )

        add_param(
            params,
            "path",
            request.get("path")
        )

    return network


def add_security_params(params, stream):

    security = stream.get("security", "none")

    add_param(params, "security", security)

    if security == "tls":

        tls = stream.get("tlsSettings") or {}

        add_param(params, "sni", tls.get("serverName"))
        add_param(params, "fp", tls.get("fingerprint"))
        add_param(params, "alpn", tls.get("alpn"))

        if tls.get("allowInsecure"):
            add_param(params, "allowInsecure", "1")

    elif security == "reality":

        reality = stream.get("realitySettings") or {}

        add_param(params, "sni", reality.get("serverName"))
        add_param(params, "fp", reality.get("fingerprint"))
        add_param(params, "pbk", reality.get("publicKey"))
        add_param(params, "sid", reality.get("shortId"))
        add_param(params, "spx", reality.get("spiderX"))

    return security


# ============================================================
# TROJAN URI BUILDER
# ============================================================

def trojan_uris_from_config(cfg, remark):

    result = []

    if not isinstance(cfg, dict):
        return result

    settings = cfg.get("settings") or {}
    servers = settings.get("servers") or []
    stream = cfg.get("streamSettings") or {}

    for index, server in enumerate(servers, 1):

        password = server.get("password")
        address = server.get("address")
        port = server.get("port")

        if not password or not address or not port:
            continue

        params = []

        add_transport_params(params, stream)
        add_security_params(params, stream)

        uri_remark = make_remark(
            remark,
            index,
            len(servers)
        )

        query = "&".join(params)

        uri = (
            f"trojan://{quote(str(password), safe='')}"
            f"@{address}:{port}"
        )

        if query:
            uri += "?" + query

        uri += "#" + quote(uri_remark, safe="")

        result.append(uri)

    return result


# ============================================================
# VLESS URI BUILDER
# ============================================================

def vless_uris_from_config(cfg, remark):

    result = []

    if not isinstance(cfg, dict):
        return result

    settings = cfg.get("settings") or {}
    vnext_list = settings.get("vnext") or []
    stream = cfg.get("streamSettings") or {}

    for vnext_index, vnext in enumerate(vnext_list, 1):

        address = vnext.get("address")
        port = vnext.get("port")
        users = vnext.get("users") or []

        if not address or not port:
            continue

        for user_index, user in enumerate(users, 1):

            user_id = user.get("id")

            if not user_id:
                continue

            params = []

            encryption = user.get("encryption", "none")
            add_param(params, "encryption", encryption)

            add_param(
                params,
                "flow",
                user.get("flow")
            )

            add_transport_params(params, stream)
            add_security_params(params, stream)

            add_param(
                params,
                "packetEncoding",
                user.get("packetEncoding")
            )

            uri_remark = remark

            if len(vnext_list) > 1 or len(users) > 1:
                uri_remark += f"-S{vnext_index}-{user_index}"

            query = "&".join(params)

            uri = (
                f"vless://{quote(str(user_id), safe='')}"
                f"@{address}:{port}"
            )

            if query:
                uri += "?" + query

            uri += "#" + quote(uri_remark, safe="")

            result.append(uri)

    return result


# ============================================================
# EXTRACT ALL CONFIGS AND ALL SERVERS
# ============================================================

def extract_all(nodes_data):

    all_configs = []
    all_uris = []
    trojan_uris = []
    vless_uris = []

    servers = (
        nodes_data or {}
    ).get("server") or []

    config_number = 0

    for server_index, server in enumerate(servers, 1):

        city = server.get("city_name") or ""
        country = server.get("country_code") or ""
        ip = server.get("ip") or ""

        base_remark = (
            f"VIF-{country}-{city}-{ip}"
        ).replace(" ", "")

        info_list = server.get("info_b") or []

        for info_index, info in enumerate(info_list, 1):

            original_config = info.get("config")
            parsed_config = parse_config(original_config)

            config_number += 1

            config_type = (
                info.get("type")
                or info.get("protocol")
                or ""
            ).lower()

            record = {
                "config_number": config_number,
                "server_index": server_index,
                "info_index": info_index,
                "country_code": country,
                "country_name": server.get("country_name"),
                "city_name": city,
                "ip": ip,
                "info_type": info.get("info_type"),
                "type": config_type,
                "original_config": original_config,
                "parsed_config": parsed_config,
            }

            all_configs.append(record)

            save_json(
                CONFIG_DIR / f"config_{config_number:03d}.json",
                record
            )

            if parsed_config is None:
                print(
                    f"[!] Config {config_number}: "
                    "не удалось разобрать JSON"
                )
                continue

            if not config_type:

                xray_settings = parsed_config.get("settings") or {}

                if xray_settings.get("servers") is not None:
                    config_type = "trojan"

                elif xray_settings.get("vnext") is not None:
                    config_type = "vless"

            remark = (
                f"{base_remark}-{config_type.upper()}"
                if config_type else base_remark
            )

            current_trojan = []
            current_vless = []

            if config_type == "trojan":

                current_trojan = trojan_uris_from_config(
                    parsed_config,
                    remark
                )

            elif config_type == "vless":

                current_vless = vless_uris_from_config(
                    parsed_config,
                    remark
                )

            else:

                current_trojan = trojan_uris_from_config(
                    parsed_config,
                    remark
                )

                current_vless = vless_uris_from_config(
                    parsed_config,
                    remark
                )

            trojan_uris.extend(current_trojan)
            vless_uris.extend(current_vless)

            all_uris.extend(current_trojan)
            all_uris.extend(current_vless)

            print(
                f"[+] Config {config_number}: "
                f"type={config_type or 'unknown'}, "
                f"Trojan={len(current_trojan)}, "
                f"VLESS={len(current_vless)}"
            )

    return (
        all_configs,
        all_uris,
        trojan_uris,
        vless_uris
    )


# ============================================================
# SAVE URI LIST
# ============================================================

def save_uris(path, uris):

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    path.write_text(
        "\n".join(uris) + ("\n" if uris else ""),
        encoding="utf-8"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 55)
    print("VIF VPN — TROJAN + VLESS EXTRACTOR")
    print("=" * 55)

    OUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    CONFIG_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    try:
        proto = Protocol(PROTOCOL)
    except Exception as error:
        print(f"[!] Protocol error: {error}")
        return 1

    dev_id = DEV_ID or str(uuid.uuid4())

    print(f"[*] DEV={dev_id}")
    print(f"[*] COUNTRY={COUNTRY}")
    print(f"[*] OUTPUT={OUT_DIR}")

    try:

        # HOST
        host = pick_host(proto, dev_id)

        print(f"[*] HOST={host}")

        # REGISTER
        print("\n[*] REGISTER")

        reg = api_post(
            host,
            "REGISTER",
            {},
            proto,
            dev_id
        )

        code = proto.real_code(
            reg.get("code")
        )

        print(f"[+] REGISTER code={code}")

        save_json(
            OUT_DIR / "register.json",
            reg
        )

        data = reg.get("data") or {}
        token = data.get("tk") or ""

        print(f"[+] UID={data.get('uid')}")
        print(f"[+] TOKEN={'получен' if token else 'отсутствует'}")

        if not token:
            raise RuntimeError(
                "REGISTER не вернул token"
            )

        # MENU
        print("\n[*] MENU")

        try:

            menu = api_post(
                host,
                "MENU",
                {},
                proto,
                dev_id,
                token
            )

            save_json(
                OUT_DIR / "menu.json",
                menu
            )

            print("[+] MENU saved")

        except Exception as error:
            print(f"[!] MENU: {error}")

        # NODES
        print("\n[*] NODES")

        body = {
            "type": "location",
            "lon": COUNTRY,
            "vip": 0
        }

        if CITY:
            body["lat"] = CITY

        nodes = api_post(
            host,
            "NODES",
            body,
            proto,
            dev_id,
            token
        )

        code = proto.real_code(
            nodes.get("code")
        )

        print(f"[+] NODES code={code}")

        save_json(
            OUT_DIR / "nodes.json",
            nodes
        )

        node_data = nodes.get("data")

        if not node_data:
            print("[!] Пустой список серверов")
            return 1

        # EXTRACT
        print("\n[*] EXTRACT ALL CONFIGS")

        (
            all_configs,
            all_uris,
            trojan_links,
            vless_links
        ) = extract_all(node_data)

        # FULL CONFIG ARCHIVE
        save_json(
            OUT_DIR / "xray_configs.json",
            all_configs
        )

        # ALL URI
        save_uris(
            OUT_DIR / "uris.txt",
            all_uris
        )

        # TROJAN ONLY
        save_uris(
            OUT_DIR / "trojan_links.txt",
            trojan_links
        )

        # VLESS ONLY
        save_uris(
            OUT_DIR / "vless_links.txt",
            vless_links
        )

        # SUMMARY
        print("\n" + "=" * 55)
        print("RESULT")
        print("=" * 55)

        print(
            f"[+] API servers: "
            f"{len(node_data.get('server') or [])}"
        )

        print(
            f"[+] Original configs: "
            f"{len(all_configs)}"
        )

        print(
            f"[+] Trojan URIs: "
            f"{len(trojan_links)}"
        )

        print(
            f"[+] VLESS URIs: "
            f"{len(vless_links)}"
        )

        print(
            f"[+] Total URIs: "
            f"{len(all_uris)}"
        )

        print("\n[*] OUTPUT FILES")

        print(f"[+] {OUT_DIR / 'uris.txt'}")
        print(f"[+] {OUT_DIR / 'trojan_links.txt'}")
        print(f"[+] {OUT_DIR / 'vless_links.txt'}")
        print(f"[+] {OUT_DIR / 'xray_configs.json'}")
        print(f"[+] {CONFIG_DIR}")

        print("\n[+] ГОТОВО")

        return 0

    except requests.RequestException as error:

        print(f"\n[!] Network error: {error}")
        return 1

    except Exception as error:

        print(f"\n[!] Ошибка: {error}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
