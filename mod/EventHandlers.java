package com.example.examplemod;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.lang.reflect.Field;
import java.util.Objects;
import java.util.Scanner;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.GuiScreen;
import net.minecraft.client.gui.inventory.GuiChest;
import net.minecraft.client.gui.inventory.GuiContainer;
import net.minecraft.client.multiplayer.PlayerControllerMP;
import net.minecraft.client.network.NetHandlerPlayClient;
import net.minecraft.network.play.client.C0DPacketCloseWindow;
import net.minecraft.network.play.client.C0EPacketClickWindow;
import net.minecraft.util.ChatComponentText;
import net.minecraftforge.client.event.ClientChatReceivedEvent;
import net.minecraftforge.client.event.GuiScreenEvent.InitGuiEvent;
import net.minecraftforge.event.CommandEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraftforge.fml.common.gameevent.TickEvent;

public class EventHandlers {
	
    public Boolean modEnabled = false;
    public File ipcFile = new File("X:\\Users\\ethan\\Desktop\\Minecraft\\Hypixel\\ipcFile");
    public Scanner ipcScanner;
    public FileWriter ipcFlusher;
    public String ipcData;
    public Integer split;
    public String uuid;
    public Long timeAvailable = 0L;
    public Boolean isSendTime = false;
    public Boolean isWindowTime = false;
    public Long nextSendTime = 0L;
    public GuiContainer chest;
    public Field clientHandler;
    public NetHandlerPlayClient netHandler;
    public String itemName;
    
    @SubscribeEvent
    public void checkFile(TickEvent event) {
    	if(modEnabled) {
    		// Check if its time to try to grab an item
    		if (isSendTime) {
    			if (System.currentTimeMillis() >= nextSendTime) {
    				isSendTime = false;
    				isWindowTime = true;
    				Minecraft.getMinecraft().thePlayer.sendChatMessage("/viewauction " + uuid);
    			}
    		} else {
	    		try {
		    		// Check that the file has data and we aren't currently trying to purchase another item
		    		if (ipcFile.length() != 0 && !isWindowTime) {
		    			// if it does, read it
		    			try {
							ipcScanner = new Scanner(ipcFile);
						} catch (FileNotFoundException e) {
							Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("Trouble reading the file, file not found"));
							modEnabled = false;
							return;
						}
		    			ipcData = ipcScanner.nextLine();
		    			ipcScanner.close();
		    			try {
							ipcFlusher = new FileWriter(ipcFile, false);
						} catch (IOException e) {
							Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("Trouble deleting the file, file not found"));
							modEnabled = false;
							return;
						}
		    			try {
		    				ipcFlusher.flush();
		        			ipcFlusher.close();
		    			} catch (IOException e) {
		    				Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("Trouble clearing the file"));
							modEnabled = false;
							return;
		    			}
		    			
		    			split = ipcData.indexOf(",");
		    			System.out.println(split);
		    			uuid = ipcData.substring(0, split);
		    			nextSendTime = Long.valueOf(ipcData.substring(split + 1));
		    			isSendTime = true;
		    			Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("Data Received"));
		    			
		    		}
	    		} catch (Exception e) {
		    		e.printStackTrace();
		    		Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("Unknown error!"));
		    	}
    		}
    	}
    }
    //TODO Handle case where the second window never appears for whatever reason
    @SubscribeEvent
    public void checkPurchaseWindow(final InitGuiEvent.Post event) {
    	if(!isWindowTime) {
    		return;
    	}
    	
    	if (event.gui instanceof GuiChest) {
    		new Thread() {
    			@Override
    			public void run() {
    				try {
    					//This is a terrible solution. In the future, it may be best to listen for incoming packets. once a guichest is opened, listen for an itemstacks packet and then do processing shit.
    					//For now, this will do. hope hypixel isnt too laggy lmao
    					chest = (GuiChest) event.gui;
    		    		//Do various checks to determine which window we are looking for.
    					
    		    		if (chest.inventorySlots.inventorySlots.size() == 54 + 36) {

    		    			//likely the purchase box
    		    			//check that the back button is present (item is an arrow)
    		    			//wait for the first slot to not be null, indicating data loaded in
    		    			Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("found big window"));
    		    			while (Objects.isNull(chest.inventorySlots.getInventory().get(31)) || chest.inventorySlots.getInventory().get(31).getItem().getRegistryName().equals("minecraft:feather")) {
    		    				Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("waiting"));
    		    				Thread.sleep(20);
    		    			}
    		    			Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText(itemName));
    		    			if (chest.inventorySlots.getInventory().get(49).getItem().getRegistryName().equals("minecraft:barrier")) {
    		    				
    		    				itemName = chest.inventorySlots.getInventory().get(31).getItem().getRegistryName();
    		    				// assume we are at the correct window, check if the item is purchaseable
    		    				Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("found puchase window"));
    		    				
    		    				if (itemName.equals("minecraft:potato")) {
    		    					Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("auction already purchased"));
    		    					netHandler.addToSendQueue(new C0EPacketClickWindow(chest.inventorySlots.windowId, 49, 0, 0, chest.inventorySlots.inventoryItemStacks.get(49), (short)1));
    		    					isWindowTime = false;
    		    				} else if (itemName.equals("minecraft:poisonous_potato")){
    		    					Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("item too expensive"));
    		    					netHandler.addToSendQueue(new C0EPacketClickWindow(chest.inventorySlots.windowId, 49, 0, 0, chest.inventorySlots.inventoryItemStacks.get(49), (short)1));
    		    					isWindowTime = false;
    		    				} else {
    		    					netHandler.addToSendQueue(new C0EPacketClickWindow(chest.inventorySlots.windowId, 31, 0, 0, chest.inventorySlots.inventoryItemStacks.get(31), (short)1));
    		    				}
    		    				
    		    				return;
    		    			} else {
    		    				Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText(chest.inventorySlots.getInventory().get(49).getItem().getRegistryName()));
    		    			}
    		    		} else if (chest.inventorySlots.inventorySlots.size() == 27 + 36) {
    		    			//likely the confirm box
    		    			//check that the back button is present 
    		    			
    		    			while (Objects.isNull(chest.inventorySlots.getInventory().get(11))) {
    		    				Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("waiting for items to load"));
    		    				Thread.sleep(20);
    		    			}
    		    			
    		    			if (chest.inventorySlots.getInventory().get(11).getItem().getRegistryName().equals("minecraft:stained_hardened_clay")) {
    		    				netHandler.addToSendQueue(new C0EPacketClickWindow(chest.inventorySlots.windowId, 11, 0, 0, chest.inventorySlots.inventoryItemStacks.get(11), (short)1));
    		    				isWindowTime = false;
    		    				Thread.sleep(100);
    		    			}
    		    		}
    				}
    				catch (Exception e) {
    					e.printStackTrace();
    				}
    			}
    		}.start();
    	}
    	
    }
    
    @SubscribeEvent
    public void toggleModEnable(CommandEvent event) {
    	if (event.command.getCommandName() == "toggleItemSearch") {
    		modEnabled = !modEnabled;
    		Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("Mod enable is now set to " + modEnabled.toString()));
    		System.out.println("Mod set to" + modEnabled.toString());
    		
    		
    		
    		if(Objects.isNull(netHandler)) {
    			String fieldName = null;
    			Field clientHandler;
    			//resolve the field the belongs to the net handler
    			Field[] fieldList = PlayerControllerMP.class.getDeclaredFields();
				for(int i = 0; i < fieldList.length; i++) {
					if (fieldList[i].getGenericType().getTypeName() == "net.minecraft.client.network.NetHandlerPlayClient") {
						fieldName = fieldList[i].getName();
					}
				}
				
				// check that the field name was resolved
				if (Objects.isNull(fieldName)) {
					Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("Failed to get field name of nethandler"));
					return;
				}
    			
				
				// get net handler
				try {
					clientHandler = PlayerControllerMP.class.getDeclaredField(fieldName);
				} catch (Exception e) {
					Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("Failed to get clienthandler field"));
					e.printStackTrace();
					return;
				}
				
				// set it to accessible and get its active instance
    			clientHandler.setAccessible(true);
            	try {
            		PlayerControllerMP pc = Minecraft.getMinecraft().playerController;
            		System.out.println(Objects.isNull(clientHandler.get(pc)));
        			netHandler = (NetHandlerPlayClient) clientHandler.get(pc);
        			//Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("got handler"));
        			Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("Grabbed Handler"));
        		} catch (Exception e) {
        			//Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("Trouble getting net handler"));
        			Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("Failed to grab handler"));
        		}
    		}

    		
    	} else if (event.command.getCommandName() == "resetState"){
    		isSendTime = false;
    		isWindowTime = false;
    		modEnabled = false;
    		Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("Reset"));
    	}
    }
    
    @SubscribeEvent
    public void handleAuctionNotFound(ClientChatReceivedEvent event) {
    	if (modEnabled && isWindowTime) {
    		if (event.message.getFormattedText().contains("This auction wasn't found!")) {
    			Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("Auction already deleted"));
    			isWindowTime = false;
    		}
    	}
    }
}
