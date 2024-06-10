package com.example.examplemod;

import net.minecraft.client.Minecraft;
import net.minecraft.util.ChatComponentText;
import net.minecraftforge.event.CommandEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraftforge.fml.common.gameevent.TickEvent;

public class newEventHandler {

	public GameStateEnum gameState;
	
	
	
	
	@SubscribeEvent
	public void loopEvent(TickEvent event) {
		switch(gameState) {
		case DISABLED:
			break;
		}
		
	}
	
	
	@SubscribeEvent
    public void handleCommands(CommandEvent event) {
		if (event.command.getCommandName() == "toggleModEnable") {
			if(gameState == gameState.DISABLED) {
				sendLocalMessage("Going into Enable State");
				gameState = gameState.ENABLED;
			} else {
				sendLocalMessage("Going into Disable State");
				gameState = gameState.DISABLED;
			}
		}
	}
	
	
	
	
	
	private void sendLocalMessage(String s) {
		Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText(s));
	}
	
}
