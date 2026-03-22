import { App, Plugin, PluginSettingTab, Setting, Notice } from 'obsidian';

interface RusticManagerSettings {
	managerUrl: string;
	minInterval: number;
	maxInterval: number;
	initInterval: number;
	heartbeatInterval: number;
}

const DEFAULT_SETTINGS: RusticManagerSettings = {
	managerUrl: 'http://localhost:8765',
	minInterval: 1.5,
	maxInterval: 5,
	initInterval: 3,
	heartbeatInterval: 1
}

export default class RusticManagerPlugin extends Plugin {
	settings: RusticManagerSettings;
	heartbeatTimer: number | null = null;
	statusBarItem: HTMLElement | null = null;

	async onload() {
		await this.loadSettings();

		this.addSettingTab(new RusticManagerSettingTab(this.app, this));

		this.statusBarItem = this.addStatusBarItem();
		this.updateStatusBar('Connecting...');

		this.startHeartbeat();

		this.registerInterval(window.setInterval(() => {
			this.sendHeartbeat();
		}, this.settings.heartbeatInterval * 60 * 1000));

		this.addCommand({
			id: 'send-heartbeat',
			name: 'Send heartbeat to Rustic Manager',
			callback: () => {
				this.sendHeartbeat();
			}
		});
	}

	onunload() {
		this.stopHeartbeat();
	}

	async loadSettings() {
		this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
	}

	async saveSettings() {
		await this.saveData(this.settings);
	}

	startHeartbeat() {
		this.sendHeartbeat();
	}

	stopHeartbeat() {
		if (this.heartbeatTimer) {
			window.clearInterval(this.heartbeatTimer);
			this.heartbeatTimer = null;
		}
	}

	async sendHeartbeat() {
		try {
			const response = await fetch(`${this.settings.managerUrl}/heartbeat`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					min: this.settings.minInterval,
					max: this.settings.maxInterval,
					init: this.settings.initInterval
				})
			});

			if (response.ok) {
				this.updateStatusBar('Connected');
			} else {
				this.updateStatusBar('Error');
			}
		} catch (error) {
			this.updateStatusBar('Offline');
		}
	}

	updateStatusBar(status: string) {
		if (this.statusBarItem) {
			this.statusBarItem.setText(`Rustic: ${status}`);
		}
	}
}

class RusticManagerSettingTab extends PluginSettingTab {
	plugin: RusticManagerPlugin;

	constructor(app: App, plugin: RusticManagerPlugin) {
		super(app, plugin);
		this.plugin = plugin;
	}

	display(): void {
		const { containerEl } = this;

		containerEl.empty();

		containerEl.createEl('h2', { text: 'Rustic Manager Settings' });

		new Setting(containerEl)
			.setName('Manager URL')
			.setDesc('Rustic Manager HTTP server URL')
			.addText(text => text
				.setPlaceholder('http://localhost:8765')
				.setValue(this.plugin.settings.managerUrl)
				.onChange(async (value) => {
					this.plugin.settings.managerUrl = value;
					await this.plugin.saveSettings();
				}));

		new Setting(containerEl)
			.setName('Min Interval (minutes)')
			.setDesc('Minimum backup interval')
			.addText(text => text
				.setPlaceholder('1.5')
				.setValue(String(this.plugin.settings.minInterval))
				.onChange(async (value) => {
					this.plugin.settings.minInterval = parseFloat(value) || 1.5;
					await this.plugin.saveSettings();
				}));

		new Setting(containerEl)
			.setName('Max Interval (minutes)')
			.setDesc('Maximum backup interval')
			.addText(text => text
				.setPlaceholder('5')
				.setValue(String(this.plugin.settings.maxInterval))
				.onChange(async (value) => {
					this.plugin.settings.maxInterval = parseFloat(value) || 5;
					await this.plugin.saveSettings();
				}));

		new Setting(containerEl)
			.setName('Init Interval (minutes)')
			.setDesc('Initial backup interval')
			.addText(text => text
				.setPlaceholder('3')
				.setValue(String(this.plugin.settings.initInterval))
				.onChange(async (value) => {
					this.plugin.settings.initInterval = parseFloat(value) || 3;
					await this.plugin.saveSettings();
				}));

		new Setting(containerEl)
			.setName('Heartbeat Interval (minutes)')
			.setDesc('How often to send heartbeat')
			.addText(text => text
				.setPlaceholder('1')
				.setValue(String(this.plugin.settings.heartbeatInterval))
				.onChange(async (value) => {
					this.plugin.settings.heartbeatInterval = parseInt(value) || 1;
					await this.plugin.saveSettings();
				}));
	}
}
