/// api_version=2
var script = registerScript({
    name: "AutoAuctionPurchase",
    version: "1.0.0",
    authors: ["7crying"]
});

var foundWindowConfirm = false;
var foundWindowPurchase = false;
var currentWindowName = "";
var targetWindowId = 0;
var windowClickPacket = Java.type("net.minecraft.network.play.client.C0EPacketClickWindow");
var windowOpenPacket = Java.type("net.minecraft.network.play.server.S2DPacketOpenWindow");
var windowItemsPacket = Java.type("net.minecraft.network.play.server.S30PacketWindowItems");
var networkManager = Java.type("net.minecraft.network.NetworkManager")
var packet;
var packetSend;
var targetItem;
script.registerModule({
    name: "AutoAuctionPurchase",
    category: "Exploit",
    description: "Automatically purchase an auction when viewed."
}, function(module) {
	
	module.on("enable", function() {
		foundWindowPurchase = false;
		foundWindowConfirm = false;
	});
	
    module.on("packet", function(eventData) {
		packet = eventData.getPacket();
		
		if(packet instanceof windowItemsPacket && foundWindowConfirm == true){
			Chat.print("sending confirm packet");
			packetSend = new windowClickPacket(targetWindowId, 11, 0, 0, packet.getItemStacks()[11], 1);
			mc.getNetHandler().addToSendQueue(packetSend);
			foundWindowConfirm = false;
		}
		
		if(packet instanceof windowItemsPacket && foundWindowPurchase == true){
			targetItem = packet.getItemStacks()[31]
			if (targetItem.getUnlocalizedName() == "item.goldNugget"){
				Chat.print("sending purchase packet");
				packetSend = new windowClickPacket(targetWindowId, 31, 0, 0, targetItem, 1);
				mc.getNetHandler().addToSendQueue(packetSend);
			}
			foundWindowPurchase = false;
		}
		
		
		if (packet instanceof windowOpenPacket){
			currentWindowName = packet.getWindowTitle().getUnformattedTextForChat();
			if(currentWindowName == "Confirm Purchase"){ //Confirm Purchase
				Chat.print("found Confirm Window");
				foundWindowConfirm = true;
				targetWindowId = packet.getWindowId(); 
			}
			if(currentWindowName == "BIN Auction View"){
				Chat.print("found Purchase Window");
				foundWindowPurchase = true;
				targetWindowId = packet.getWindowId();
			}
		}
		
    });
	

});