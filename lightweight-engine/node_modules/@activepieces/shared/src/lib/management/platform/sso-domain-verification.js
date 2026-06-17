"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SsoDomainVerification = exports.SsoDomainVerificationRecord = exports.SsoDomainVerificationRecordType = exports.SsoDomainVerificationStatus = void 0;
const zod_1 = require("zod");
var SsoDomainVerificationStatus;
(function (SsoDomainVerificationStatus) {
    SsoDomainVerificationStatus["PENDING_VERIFICATION"] = "PENDING_VERIFICATION";
    SsoDomainVerificationStatus["VERIFIED"] = "VERIFIED";
})(SsoDomainVerificationStatus || (exports.SsoDomainVerificationStatus = SsoDomainVerificationStatus = {}));
var SsoDomainVerificationRecordType;
(function (SsoDomainVerificationRecordType) {
    SsoDomainVerificationRecordType["TXT"] = "TXT";
})(SsoDomainVerificationRecordType || (exports.SsoDomainVerificationRecordType = SsoDomainVerificationRecordType = {}));
exports.SsoDomainVerificationRecord = zod_1.z.object({
    type: zod_1.z.enum([SsoDomainVerificationRecordType.TXT]),
    name: zod_1.z.string(),
    value: zod_1.z.string(),
});
exports.SsoDomainVerification = zod_1.z.object({
    status: zod_1.z.enum([
        SsoDomainVerificationStatus.PENDING_VERIFICATION,
        SsoDomainVerificationStatus.VERIFIED,
    ]),
    record: exports.SsoDomainVerificationRecord,
    createdAt: zod_1.z.string(),
});
//# sourceMappingURL=sso-domain-verification.js.map