import base64


def ip4_2_int(ip):
    a = ip.split(".")[0]
    b = ip.split(".")[1]
    c = ip.split(".")[2]
    d = ip.split(".")[3].split(":")[0]
    e = ip.split(":")[1]
    return int(a) + int(b)*256**1 + int(c)*256**2 + int(d)*256**3 + int(e)*256**4


def int_2_ip4(num):
    e = num % 256
    num //= 256
    d = num % 256
    num //= 256
    c = num % 256
    num //= 256
    b = num % 256
    num //= 256
    a = num
    return f"{e}.{d}.{c}.{b}:{a}"


def expand_ipv6(ip):
    parts = ip.split(":")
    num_parts = len(parts)
    num_empty = parts.count('')
    if num_empty > 1:
        raise ValueError("Invalid IPv6 address")
    if num_empty == 1:
        num_missing = 8 - num_parts + 1
        parts.remove('')
        parts.extend(['0000'] * num_missing)
    return ":".join(parts)


int_2_64_table = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ/="


def int_to_base64(num):
    if num == 0:
        return int_2_64_table[0]
    result = ""
    while num:
        result = int_2_64_table[num % len(int_2_64_table)] + result
        num //= len(int_2_64_table)
    return result


def base64_to_int(base64_str):
    num = 0
    for char in base64_str:
        num = num * len(int_2_64_table) + int_2_64_table.index(char)
    return num


def base64_2_ip6(ip_full):
    ip_port = ip_full[0:4]
    ip = f"{hex(base64_to_int(ip_full[4:]))[2:]:0>32}"
    return f"[{ip[0:4]}:{ip[4:8]}:{ip[8:12]}:{ip[12:16]}:{ip[16:20]}:{ip[20:24]}:{ip[24:28]}:{ip[28:32]}]:{base64_to_int(ip_port)}"


def base64_2_domain(ip_full):
    ip_port = base64_to_int(ip_full[0:4])
    domain = base64.b64decode(ip_full[4:]).decode()
    return f"{domain}:{ip_port}"


def base64_2_ip(ip):
    if (":" in ip):
        return ip
    if (ip[0] == "0"):
        return int_2_ip4(base64_to_int(ip[1:]))
    elif (ip[0] == "1"):
        return base64_2_ip6(ip[1:])
    else:
        return base64_2_domain(ip[1:])


def ip4_2_base64(ip):
    return "0"+int_to_base64(ip4_2_int(ip))


def ip6_2_base64(ip):
    return "1" + f"{int_to_base64(int(ip.split(":")[-1])):0>4}"+(int_to_base64(int(expand_ipv6(ip.split("]")[0].split("[")[1]).replace(":", ""), 16)))


def domain_2_base64(ip):
    return "2" + f"{int_to_base64(int(ip.split(":")[-1])):0>4}"+base64.b64encode(ip.split(":")[0].encode()).decode()


def ip_2_base64(ip):
    if (ip[0] == "["):
        return ip6_2_base64(ip)
    elif (ip.replace(".", "").replace(":", "").isdigit()):
        return ip4_2_base64(ip)
    else:
        return domain_2_base64(ip)


# print(ip_2_base64("192.168.1.1:8080"))
# print(base64_2_ip("07V010qz0"))
# print(ip_2_base64("[2001:0db8:85a3:0000:0000:8a2e:0370:7334]:1234"))
# print(base64_2_ip("100jiw0gSUxqc00000yyU3s7cQ"))
# print(ip_2_base64("example.com:8080"))
# print(base64_2_ip("201/gZXhhbXBsZS5jb20="))

# """
# 07V010qz0
# 192.168.1.1:8080
# 100jiw0gSUxqc00000yyU3s7cQ
# [2001:0db8:85a3:0000:0000:8a2e:0370:7334]:1234
# 201/gZXhhbXBsZS5jb20=
# example.com:8080
# 2006XbmV1dHJvbi5jeHlrZXZpbi50b3A=
# """
