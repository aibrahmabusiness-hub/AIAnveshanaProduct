"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.PieceCategory = exports.PiecePackage = exports.PublicPiecePackage = exports.CustomNpmPiecePackage = exports.OfficialPiecePackage = exports.PrivatePiecePackage = exports.PieceType = exports.PackageType = void 0;
const zod_1 = require("zod");
var PackageType;
(function (PackageType) {
    PackageType["ARCHIVE"] = "ARCHIVE";
    PackageType["REGISTRY"] = "REGISTRY";
})(PackageType || (exports.PackageType = PackageType = {}));
var PieceType;
(function (PieceType) {
    PieceType["CUSTOM"] = "CUSTOM";
    PieceType["OFFICIAL"] = "OFFICIAL";
})(PieceType || (exports.PieceType = PieceType = {}));
exports.PrivatePiecePackage = zod_1.z.object({
    packageType: zod_1.z.literal(PackageType.ARCHIVE),
    pieceType: zod_1.z.nativeEnum(PieceType),
    pieceName: zod_1.z.string(),
    pieceVersion: zod_1.z.string(),
    archiveId: zod_1.z.string(),
    platformId: zod_1.z.string(),
});
exports.OfficialPiecePackage = zod_1.z.object({
    packageType: zod_1.z.literal(PackageType.REGISTRY),
    pieceType: zod_1.z.literal(PieceType.OFFICIAL),
    pieceName: zod_1.z.string(),
    pieceVersion: zod_1.z.string(),
});
exports.CustomNpmPiecePackage = zod_1.z.object({
    packageType: zod_1.z.literal(PackageType.REGISTRY),
    pieceType: zod_1.z.literal(PieceType.CUSTOM),
    pieceName: zod_1.z.string(),
    pieceVersion: zod_1.z.string(),
    platformId: zod_1.z.string(),
});
exports.PublicPiecePackage = zod_1.z.union([exports.OfficialPiecePackage, exports.CustomNpmPiecePackage]);
exports.PiecePackage = zod_1.z.union([exports.PrivatePiecePackage, exports.OfficialPiecePackage, exports.CustomNpmPiecePackage]);
var PieceCategory;
(function (PieceCategory) {
    PieceCategory["ARTIFICIAL_INTELLIGENCE"] = "ARTIFICIAL_INTELLIGENCE";
    PieceCategory["COMMUNICATION"] = "COMMUNICATION";
    PieceCategory["COMMERCE"] = "COMMERCE";
    PieceCategory["CORE"] = "CORE";
    PieceCategory["UNIVERSAL_AI"] = "UNIVERSAL_AI";
    PieceCategory["FLOW_CONTROL"] = "FLOW_CONTROL";
    PieceCategory["BUSINESS_INTELLIGENCE"] = "BUSINESS_INTELLIGENCE";
    PieceCategory["ACCOUNTING"] = "ACCOUNTING";
    PieceCategory["PRODUCTIVITY"] = "PRODUCTIVITY";
    PieceCategory["CONTENT_AND_FILES"] = "CONTENT_AND_FILES";
    PieceCategory["DEVELOPER_TOOLS"] = "DEVELOPER_TOOLS";
    PieceCategory["CUSTOMER_SUPPORT"] = "CUSTOMER_SUPPORT";
    PieceCategory["FORMS_AND_SURVEYS"] = "FORMS_AND_SURVEYS";
    PieceCategory["HUMAN_RESOURCES"] = "HUMAN_RESOURCES";
    PieceCategory["PAYMENT_PROCESSING"] = "PAYMENT_PROCESSING";
    PieceCategory["MARKETING"] = "MARKETING";
    PieceCategory["SALES_AND_CRM"] = "SALES_AND_CRM";
})(PieceCategory || (exports.PieceCategory = PieceCategory = {}));
//# sourceMappingURL=piece.js.map