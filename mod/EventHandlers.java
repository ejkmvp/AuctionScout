package com.example.examplemod;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.lang.reflect.Field;
import java.util.Objects;
import java.util.Scanner;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.inventory.GuiChest;
import net.minecraft.client.gui.inventory.GuiContainer;
import net.minecraft.client.multiplayer.PlayerControllerMP;
import net.minecraft.client.network.NetHandlerPlayClient;
import net.minecraft.network.play.client.C0EPacketClickWindow;
import net.minecraft.util.ChatComponentText;
import net.minecraftforge.client.event.GuiOpenEvent;
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
    		}
    		
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
    			
    		}
    	}
    }
    
    @SubscribeEvent
    public void checkPurchaseWindow(GuiOpenEvent event) {
    	//TEST CODE
    	/*
    	if (event.gui instanceof GuiChest) {
    		Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("found window"));
    		Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("chest size is " + String.valueOf(((GuiChest) event.gui).inventorySlots.inventorySlots.size())));
    		//((GuiChest) event.gui).inventorySlots.slotClick(12, 0, 0, Minecraft.getMinecraft().thePlayer);
    		//((GuiChest) event.gui).inventorySlots.transferStackInSlot(Minecraft.getMinecraft().thePlayer, 13);
    		//Minecraft.getMinecraft().playerController.windowClick(((GuiChest) event.gui).inventorySlots.windowId, 13, 0, 2, Minecraft.getMinecraft().thePlayer);
    		//Minecraft.getMinecraft().playerController.windowClick(Minecraft.getMinecraft().thePlayer.inventoryContainer.windowId, 13, 0, 0, Minecraft.getMinecraft().thePlayer);
    		netHandler.addToSendQueue(new C0EPacketClickWindow(((GuiChest) event.gui).inventorySlots.windowId, 11, 0, 0, ((GuiChest) event.gui).inventorySlots.getSlot(11).getStack(), (short) 1));
    		//netHandler.addToSendQueue(new S00PacketDisconnect());
    		//netHandler.addToSendQueue(new S40PacketDisconnect());
    	}
    	
    	
    	//TEST CODE
    	if(!isWindowTime) {
    		return;
    	}
    	*/
    	if (event.gui instanceof GuiChest) {
    		chest = (GuiChest) event.gui;
    		//Do various checks to determine which window we are looking for.
    		if (chest.inventorySlots.inventorySlots.size() == 54 + 36) {
    			//likely the purchase box
    			//check that the back button is present (item is an arrow)
    			if (!Objects.isNull(chest.inventorySlots.getSlot(49).getStack()) && chest.inventorySlots.getSlot(49).getStack().getItem().getRegistryName() == "minecraft:arrow") {
    				// assume we are at the correct window, send click to the gold nugget
    				Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("found puchase window"));
    				//chest.inventorySlots.slotClick(31, 0, 1, Minecraft.getMinecraft().thePlayer);
    				netHandler.addToSendQueue(new C0EPacketClickWindow(chest.inventorySlots.windowId, 31, 0, 0, chest.inventorySlots.inventoryItemStacks.get(31), (short)1));
    				return;
    			}
    		} else if (chest.inventorySlots.inventorySlots.size() == 27 + 36) {
    			//likely the confirm box
    			//check that the back button is present 
    			if (!Objects.isNull(chest.inventorySlots.getSlot(11).getStack()) && chest.inventorySlots.getSlot(11).getStack().getItem().getRegistryName() == "minecraft:stained_hardened_clay") {
    				//chest.inventorySlots.slotClick(11, 0, 1, Minecraft.getMinecraft().thePlayer);
    				isWindowTime = false;
    			}
    		}
    	}
    	
    }
    
    @SubscribeEvent
    public void toggleModEnable(CommandEvent event) {
    	if (event.command.getCommandName() == "toggleItemSearch") {
    		modEnabled = !modEnabled;
    		Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("Mod enable is now set to " + modEnabled.toString()));
    		System.out.println("Mod set to" + modEnabled.toString());
    		
    		if(Objects.isNull(netHandler)) {
    			Field clientHandler;
				try {
					
					Field[] fieldList = PlayerControllerMP.class.getDeclaredFields();
					for(int i = 0; i < fieldList.length; i++) {
						//TODO use the getTypeName to find which obfuscated name belongs to the "net.minecraft.client.network.NetHandlerPlayClient"
						System.out.println(fieldList[i].getName());
						System.out.println(fieldList[i].getGenericType().getTypeName());
					}
					clientHandler = PlayerControllerMP.class.getDeclaredField("netClientHandler");
				} catch (Exception e) {
					Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText("Failed to get clienthandler field"));
					e.printStackTrace();
					return;
				}
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

    		
    	} else {
    		System.out.println(event.command.getCommandName());
    	}
    }
}
