"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getPieceMajorAndMinorVersion = void 0;
const tslib_1 = require("tslib");
const major_1 = tslib_1.__importDefault(require("semver/functions/major"));
const minor_1 = tslib_1.__importDefault(require("semver/functions/minor"));
const min_version_1 = tslib_1.__importDefault(require("semver/ranges/min-version"));
const getPieceMajorAndMinorVersion = (pieceVersion) => {
    const minimumSemver = (0, min_version_1.default)(pieceVersion);
    return minimumSemver
        ? `${(0, major_1.default)(minimumSemver)}.${(0, minor_1.default)(minimumSemver)}`
        : `${(0, major_1.default)(pieceVersion)}.${(0, minor_1.default)(pieceVersion)}`;
};
exports.getPieceMajorAndMinorVersion = getPieceMajorAndMinorVersion;
//# sourceMappingURL=version-utils.js.map