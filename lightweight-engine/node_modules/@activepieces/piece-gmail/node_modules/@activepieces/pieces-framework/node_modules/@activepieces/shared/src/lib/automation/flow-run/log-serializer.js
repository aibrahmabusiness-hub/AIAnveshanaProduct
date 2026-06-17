"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.logSerializer = void 0;
const tslib_1 = require("tslib");
const step_output_1 = require("./execution/step-output");
exports.logSerializer = {
    serialize(log) {
        return tslib_1.__awaiter(this, void 0, void 0, function* () {
            const withVersion = log.version
                ? log
                : Object.assign(Object.assign({}, log), { version: step_output_1.FLOW_RUN_LOG_MANIFEST_V2 });
            return Buffer.from(JSON.stringify(withVersion, null));
        });
    },
};
//# sourceMappingURL=log-serializer.js.map