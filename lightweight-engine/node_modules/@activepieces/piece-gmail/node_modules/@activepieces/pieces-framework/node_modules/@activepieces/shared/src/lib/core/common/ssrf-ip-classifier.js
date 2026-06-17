"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ssrfIpClassifier = void 0;
const tslib_1 = require("tslib");
const ipaddr_js_1 = tslib_1.__importDefault(require("ipaddr.js"));
function parseOrNull(ip) {
    try {
        return ipaddr_js_1.default.parse(ip);
    }
    catch (_a) {
        return null;
    }
}
function isInAllowList({ ip, allowList }) {
    if (allowList.includes(ip))
        return true;
    const addr = parseOrNull(ip);
    if (!addr)
        return false;
    return allowList.some((entry) => entry.includes('/') && matchesCidr({ addr, cidr: entry }));
}
function matchesCidr({ addr, cidr }) {
    try {
        const range = ipaddr_js_1.default.parseCIDR(cidr);
        if (addr.kind() !== range[0].kind())
            return false;
        return addr.match(range);
    }
    catch (_a) {
        return false;
    }
}
function isBlockedRange(addr) {
    if (addr.kind() === 'ipv6') {
        const v6 = addr;
        if (v6.isIPv4MappedAddress()) {
            return isBlockedRange(v6.toIPv4Address());
        }
    }
    return addr.range() !== 'unicast';
}
function isBlockedIp({ ip, allowList }) {
    if (isInAllowList({ ip, allowList })) {
        return false;
    }
    const addr = parseOrNull(ip);
    if (!addr) {
        return true;
    }
    return isBlockedRange(addr);
}
exports.ssrfIpClassifier = {
    isBlockedIp,
};
//# sourceMappingURL=ssrf-ip-classifier.js.map