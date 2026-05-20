/** @odoo-module **/

import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class WhapiInbox extends Component {
    static template = "whatsapp_whapi.WhapiInbox";
    static props = ["*"];

    setup() {
        this.orm = useService("orm");
        this.notification = useService("notification");
        this.state = useState({
            channelId: this.props.action?.params?.channel_id || null,
            channels: [],
            chats: [],
            messages: [],
            selectedChatId: null,
            composerText: "",
            messageType: "text",
            loading: true,
        });
        onWillStart(async () => {
            await this.loadChannels();
            if (this.state.channelId) {
                await this.loadInbox();
            }
            this.state.loading = false;
        });
    }

    async loadChannels() {
        const channels = await this.orm.searchRead(
            "whatsapp.channel",
            [["active", "=", true]],
            ["id", "name", "state", "phone"]
        );
        this.state.channels = channels;
        if (!this.state.channelId && channels.length) {
            this.state.channelId = channels[0].id;
        }
    }

    async loadInbox() {
        if (!this.state.channelId) return;
        const data = await this.orm.call(
            "whatsapp.message",
            "get_inbox_data",
            [this.state.channelId, this.state.selectedChatId]
        );
        this.state.chats = data.chats || [];
        this.state.messages = data.messages || [];
    }

    async onChannelChange(ev) {
        this.state.channelId = parseInt(ev.target.value, 10);
        this.state.selectedChatId = null;
        await this.loadInbox();
    }

    async selectChat(chatId) {
        this.state.selectedChatId = chatId;
        const data = await this.orm.call(
            "whatsapp.message",
            "get_inbox_data",
            [this.state.channelId, chatId]
        );
        this.state.messages = data.messages || [];
    }

    async sendMessage() {
        if (!this.state.composerText.trim() || !this.state.selectedChatId) {
            this.notification.add("Select a chat and enter a message.", { type: "warning" });
            return;
        }
        await this.orm.call(
            "whatsapp.message",
            "send_message",
            [
                this.state.channelId,
                this.state.selectedChatId,
                this.state.messageType,
            ],
            { body: this.state.composerText }
        );
        this.state.composerText = "";
        await this.loadInbox();
        this.notification.add("Message sent.", { type: "success" });
    }

    formatTime(iso) {
        if (!iso) return "";
        try {
            return new Date(iso).toLocaleString();
        } catch {
            return iso;
        }
    }

    onComposerKeydown(ev) {
        if (ev.key === "Enter") {
            ev.preventDefault();
            this.sendMessage();
        }
    }
}

registry.category("actions").add("whatsapp_whapi.inbox", WhapiInbox);
