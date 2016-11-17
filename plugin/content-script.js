function notifyExtension() {
  browser.runtime.sendMessage({"url": this.document.URL});
}
notifyExtension();
