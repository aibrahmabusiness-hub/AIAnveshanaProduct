"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports._updateSampleDataInfo = void 0;
const tslib_1 = require("tslib");
const dayjs_1 = tslib_1.__importDefault(require("dayjs"));
const flow_structure_util_1 = require("../util/flow-structure-util");
const _updateSampleDataInfo = (flowVersion, request) => {
    return flow_structure_util_1.flowStructureUtil.transferFlow(flowVersion, (step) => {
        if (step.name !== request.stepName) {
            return step;
        }
        return Object.assign(Object.assign({}, step), { settings: Object.assign(Object.assign({}, step.settings), { sampleData: request.sampleDataSettings ? Object.assign(Object.assign({}, request.sampleDataSettings), { lastTestDate: (0, dayjs_1.default)().toISOString() }) : undefined }) });
    });
};
exports._updateSampleDataInfo = _updateSampleDataInfo;
//# sourceMappingURL=update-sample-data-info.js.map