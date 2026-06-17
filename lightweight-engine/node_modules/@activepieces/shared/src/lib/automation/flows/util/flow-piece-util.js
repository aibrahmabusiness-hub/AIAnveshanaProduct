"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.flowPieceUtil = void 0;
const action_1 = require("../actions/action");
const trigger_1 = require("../triggers/trigger");
const flow_structure_util_1 = require("../util/flow-structure-util");
exports.flowPieceUtil = {
    getExactVersion(pieceVersion) {
        if (pieceVersion.startsWith('^') || pieceVersion.startsWith('~')) {
            return pieceVersion.slice(1);
        }
        return pieceVersion;
    },
    getUsedPieces(trigger) {
        return flow_structure_util_1.flowStructureUtil.getAllSteps(trigger)
            .filter((step) => step.type === action_1.FlowActionType.PIECE || step.type === trigger_1.FlowTriggerType.PIECE)
            .map((step) => step.settings.pieceName);
    },
};
//# sourceMappingURL=flow-piece-util.js.map