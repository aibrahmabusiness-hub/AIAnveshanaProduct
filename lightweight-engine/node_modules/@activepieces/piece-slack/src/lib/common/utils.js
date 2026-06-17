"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.slackSendMessage = void 0;
exports.textToSectionBlocks = textToSectionBlocks;
exports.buildFlowOriginContextBlock = buildFlowOriginContextBlock;
exports.processMessageTimestamp = processMessageTimestamp;
exports.getFirstFiveOrAll = getFirstFiveOrAll;
exports.parseCommand = parseCommand;
const tslib_1 = require("tslib");
const web_api_1 = require("@slack/web-api");
const SLACK_SECTION_TEXT_MAX_LENGTH = 3000;
function textToSectionBlocks(text) {
    if (text.length <= SLACK_SECTION_TEXT_MAX_LENGTH) {
        return [{ type: 'section', text: { type: 'mrkdwn', text } }];
    }
    const blocks = [];
    let remaining = text;
    while (remaining.length > 0) {
        if (remaining.length <= SLACK_SECTION_TEXT_MAX_LENGTH) {
            blocks.push({ type: 'section', text: { type: 'mrkdwn', text: remaining } });
            break;
        }
        let splitIndex = remaining.lastIndexOf('\n', SLACK_SECTION_TEXT_MAX_LENGTH);
        if (splitIndex <= 0) {
            splitIndex = remaining.lastIndexOf(' ', SLACK_SECTION_TEXT_MAX_LENGTH);
        }
        if (splitIndex <= 0) {
            splitIndex = SLACK_SECTION_TEXT_MAX_LENGTH;
        }
        blocks.push({ type: 'section', text: { type: 'mrkdwn', text: remaining.substring(0, splitIndex) } });
        remaining = remaining.substring(splitIndex).trimStart();
    }
    return blocks;
}
function buildFlowOriginContextBlock(context) {
    return {
        type: 'context',
        elements: [
            {
                type: 'mrkdwn',
                text: `Message sent by <${new URL(context.server.publicUrl).origin}/projects/${context.project.id}/flows/${context.flows.current.id}|this flow>.`
            }
        ]
    };
}
const slackSendMessage = (_a) => tslib_1.__awaiter(void 0, [_a], void 0, function* ({ text, conversationId, username, profilePicture, iconEmoji, blocks, threadTs, token, file, replyBroadcast, unfurlLinks, }) {
    const client = new web_api_1.WebClient(token);
    if (file) {
        return yield client.files.uploadV2({
            channel_id: conversationId,
            initial_comment: text,
            thread_ts: threadTs,
            file_uploads: [
                {
                    file: file.data,
                    filename: file.filename,
                },
            ],
        });
    }
    else {
        const messageParams = {
            text,
            channel: conversationId,
            username,
            icon_url: profilePicture,
            icon_emoji: iconEmoji,
            blocks: blocks,
            thread_ts: threadTs,
        };
        if (replyBroadcast) {
            messageParams.reply_broadcast = replyBroadcast;
        }
        if (unfurlLinks === false) {
            messageParams.unfurl_links = false;
        }
        return yield client.chat.postMessage(messageParams);
    }
});
exports.slackSendMessage = slackSendMessage;
function processMessageTimestamp(input) {
    // Regular expression to match a URL containing the timestamp
    const urlRegex = /\/p(\d+)(\d{6})$/;
    // Check if the input is a URL
    const urlMatch = input.match(urlRegex);
    if (urlMatch) {
        const timestamp = `${urlMatch[1]}.${urlMatch[2]}`;
        return timestamp;
    }
    // Check if the input is already in the desired format
    const timestampRegex = /^(\d+)\.(\d{6})$/;
    const timestampMatch = input.match(timestampRegex);
    if (timestampMatch) {
        return input;
    }
    return undefined;
}
function getFirstFiveOrAll(array) {
    if (array.length <= 5) {
        return array;
    }
    else {
        return array.slice(0, 5);
    }
}
/**
* Parse a message text to extract command and arguments
*/
function parseCommand(text, botUserId, validCommands) {
    if (!botUserId) {
        return null;
    }
    // Check if the message mentions the bot
    const mentionRegex = new RegExp(`<@${botUserId}>\\s+(.+)`, 's');
    const mentionMatch = text.match(mentionRegex);
    if (!mentionMatch) {
        return null;
    }
    // Extract the text after the mention
    const commandText = mentionMatch[1].trim();
    // Split into command and arguments (first word is command, rest are args)
    const parts = commandText.split(/\s+/);
    const command = parts[0].toLowerCase();
    const args = parts.slice(1);
    // Check if it's a valid command
    if (!validCommands.includes(command)) {
        return null;
    }
    return {
        command,
        args,
    };
}
//# sourceMappingURL=utils.js.map