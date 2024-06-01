package com.example.examplemod;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Scanner;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.inventory.GuiChest;
import net.minecraft.client.gui.inventory.GuiContainer;
import net.minecraft.init.Blocks;
import net.minecraft.util.ChatComponentText;
import net.minecraftforge.client.ClientCommandHandler;
import net.minecraftforge.client.event.GuiOpenEvent;
import net.minecraftforge.event.CommandEvent;
import net.minecraftforge.fml.common.Mod.EventHandler;
import net.minecraftforge.fml.common.event.FMLInitializationEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraftforge.fml.common.gameevent.TickEvent;

public class EventHandlers {
    public Boolean modEnabled = true;
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
    	System.out.println("g");
    	if(!isWindowTime) {
    		return;
    	}
    	if (event.gui instanceof GuiChest) {
    		chest = (GuiChest) event.gui;
    		//Do various checks to determine which window we are looking for.
    		if (chest.inventorySlots.inventorySlots.size() == 54) {
    			//likely the purchase box
    			//check that the back button is present (item is an arrow)
    			if (chest.inventorySlots.getSlot(49).getStack().getItem().getRegistryName() == "minecraft:arrow") {
    				// assume we are at the correct window, send click to the gold nugget
    				chest.inventorySlots.slotClick(31, 0, 1, Minecraft.getMinecraft().thePlayer);
    				return;
    			}
    		} else if (chest.inventorySlots.inventorySlots.size() == 27) {
    			//likely the confirm box
    			//check that the back button is present 
    			if (chest.inventorySlots.getSlot(11).getStack().getItem().getRegistryName() == "minecraft:stained_hardened_clay") {
    				chest.inventorySlots.slotClick(11, 0, 1, Minecraft.getMinecraft().thePlayer);
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
    		Minecraft.getMinecraft().thePlayer.sendChatMessage("Mod enable is now set to " + modEnabled.toString());
    		System.out.println("Mod set to" + modEnabled.toString());
    	} else {
    		System.out.println(event.command.getCommandName());
    	}
    }
}
