package com.example.examplemod;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.lang.reflect.Field;
import java.util.Objects;
import java.util.Scanner;
import java.util.function.Consumer;
import java.util.function.Predicate;

import net.minecraft.client.Minecraft;
import net.minecraft.client.gui.inventory.GuiChest;
import net.minecraft.client.multiplayer.PlayerControllerMP;
import net.minecraft.client.network.NetHandlerPlayClient;
import net.minecraft.item.ItemStack;
import net.minecraft.network.play.client.C0EPacketClickWindow;
import net.minecraft.scoreboard.ScorePlayerTeam;
import net.minecraft.scoreboard.Scoreboard;
import net.minecraft.util.ChatComponentText;
import net.minecraftforge.client.event.ClientChatReceivedEvent;
import net.minecraftforge.client.event.GuiScreenEvent.InitGuiEvent;
import net.minecraftforge.event.CommandEvent;
import net.minecraftforge.fml.common.eventhandler.SubscribeEvent;
import net.minecraftforge.fml.common.gameevent.TickEvent;

public class newEventHandler {

	public GameStateEnum gameState;
    public NetHandlerPlayClient netHandler;
    public File ipcFile = new File("X:\\Users\\ethan\\Desktop\\Minecraft\\Hypixel\\ipcFile");
    public Scanner ipcScanner;
    public FileWriter ipcFlusher;
    public String ipcData;
    public Integer split;
    public String uuid;
    public Long nextSendTime = 0L;
    public Long sendExpireTime = 0L;
    public GameStateEnum tempLocation;
    public GuiChest chest;
    public Long lastPacketSendTime = 0L;
    
	@SubscribeEvent
	public void loopEvent(TickEvent event) {
		// Check that we are still on a server
		checkServerStatus();
		switch(gameState) {
		case DISABLED:
			// reset a lot of vars
			nextSendTime = 0L;
			sendExpireTime = 0L;
			tempLocation = null;
			chest = null;
			lastPacketSendTime = null;
			netHandler = null;
			break;
		case ONSERVER:
			// print out game state
			printGameState();
			// resolve nethandler if necessary
			if (netHandler == null) {
				getNetHandler();
				break;
			}
			// check location to determine which state to go to
			gameState = getLocation();
			break;
		case AUCTIONHOUSE:
		case HUB:
			// print out game state
			printGameState();
			// check if the ipc file has content ready to process
			checkFile();
			// verify we are still in a valid state to continue
			gameState = getLocation();
			break;
		case COMMANDREADY:
			// print out game state
			printGameState();
			// wait untill its time to send the command 
			if (System.currentTimeMillis() >= nextSendTime) {
				// send view auction command
				Minecraft.getMinecraft().thePlayer.sendChatMessage("/viewauction " + uuid);
				// set the expiration time for the next state
				sendExpireTime = System.currentTimeMillis() + 1000;
				gameState = gameState.COMMANDSENT;
			}
			// verify we are still in a valid state
			tempLocation = getLocation();
			if (tempLocation == gameState.DISABLED || tempLocation == gameState.ONSERVER) {
				gameState = tempLocation;
			}
			break;
		case COMMANDSENT:
			// print out game state
			printGameState();
			//Everything in this state should be triggered via events, so just wait until expiration time
			if(System.currentTimeMillis() >= sendExpireTime) {
				sendLocalMessage("Failed to handle sent auction message, disabling mod...");
				gameState = gameState.DISABLED;
			}
			break;
		case EXITFIRSTWINDOW:
			// print out game state
			printGameState();
			// check if the current screen is longer the chest
			if(!(Minecraft.getMinecraft().currentScreen instanceof GuiChest)) {
				sendLocalMessage("Exited Big Window");
				gameState = gameState.ONSERVER;
				return;
			}
			// send click packet on "close" slot
			if(System.currentTimeMillis() >= lastPacketSendTime) {
				sendChestClickPacket(chest.inventorySlots.windowId, 49, chest.inventorySlots.inventoryItemStacks.get(49));
				lastPacketSendTime = System.currentTimeMillis() + 50;
			}
			// expiration timer
			if (System.currentTimeMillis() >= sendExpireTime) {
				sendLocalMessage("Failed to handle closing big window, disabling...");
				gameState = gameState.DISABLED;
			}
			break;
		case CONTINUEFIRSTWINDOW:
			// print out game state
			printGameState();
			// send click packet on "Purchase' slot
			if(System.currentTimeMillis() >= lastPacketSendTime) {
				sendChestClickPacket(chest.inventorySlots.windowId, 31, chest.inventorySlots.inventoryItemStacks.get(31));
				lastPacketSendTime = System.currentTimeMillis() + 50;
			}
			// expiration timer
			if (System.currentTimeMillis() >= sendExpireTime) {
				sendLocalMessage("Failed to handle continuing from big window, disabling...");
				gameState = gameState.DISABLED;
			}	
			break;
		case SECONDWINDOW:
			// print out game state
			printGameState();
			// Everything in this state should be triggered by events, so just check expiration time
			if (System.currentTimeMillis() >= sendExpireTime) {
				sendLocalMessage("Failed to handle small window recognition, disabling...");
				gameState = gameState.DISABLED;
			}	
			break;
		case CONTINUESECONDWINDOW:
			// print out game state
			printGameState();
			// check that the small window was closed
			if(!(Minecraft.getMinecraft().currentScreen instanceof GuiChest)) {
				sendLocalMessage("Exited Small Window");
				gameState = gameState.ONSERVER;
				return;
			}
			// expiration timer
			if (System.currentTimeMillis() >= sendExpireTime) {
				sendLocalMessage("Failed to handle continuing from small window, disabling...");
				gameState = gameState.DISABLED;
			}
			// send click packet on accept button
			if(System.currentTimeMillis() >= lastPacketSendTime) {
				sendChestClickPacket(chest.inventorySlots.windowId, 11, chest.inventorySlots.inventoryItemStacks.get(11));
				lastPacketSendTime = System.currentTimeMillis() + 50;
			}
			break;
		}
	}
	
	
	@SubscribeEvent
	public void checkPurchaseWindow(final InitGuiEvent.Post event) {
		if (!(event.gui instanceof GuiChest)) {
			return;
		}
		chest = (GuiChest) event.gui;
		// check if we're in the proper state to handle the inital purchase window
		if (gameState == gameState.COMMANDSENT) {
			// check the chest size is correct
			if (chest.inventorySlots.inventorySlots.size() == 54 + 36) {
				//Assume that we found the right chest. 
				sendLocalMessage("Found Purchase Window");
				sendExpireTime = System.currentTimeMillis() + 1000;
				// Spin up a thread to handle parsing the chest's contents
				new Thread() {
	    			@Override
	    			public void run() {
	    				// Wait for chest to populate with items
	    				while (Objects.isNull(chest.inventorySlots.getInventory().get(31)) || chest.inventorySlots.getInventory().get(31).getItem().getRegistryName().equals("minecraft:feather")) {
		    				sendLocalMessage("Waiting...");
		    				try {
								Thread.sleep(20);
							} catch (InterruptedException e) {
								e.printStackTrace();
								sendLocalMessage("Thread interrupted while sleeping, disabling mod");
								gameState = gameState.DISABLED;
								return;
							}
		    			}
		    			// Final check to verify that we are in the correct window
		    			if (chest.inventorySlots.getInventory().get(49).getItem().getRegistryName().equals("minecraft:barrier")) {
		    				String itemName = chest.inventorySlots.getInventory().get(31).getItem().getRegistryName();
		    				if (itemName.equals("minecraft:potato")) {
		    					sendLocalMessage("Item Already Purchased");
		    					sendExpireTime = System.currentTimeMillis() + 1000;
		    					gameState = gameState.EXITFIRSTWINDOW;
		    				} else if (itemName.equals("minecraft:poisonous_potato")){
		    					sendLocalMessage("Item too expensive");
		    					sendExpireTime = System.currentTimeMillis() + 1000;
		    					gameState = gameState.EXITFIRSTWINDOW;
		    				} else {
		    					sendExpireTime = System.currentTimeMillis() + 1000;
		    					gameState = gameState.CONTINUEFIRSTWINDOW;
		    				}
		    				return;
		    			} else {
		    				sendLocalMessage("Unexpected item found in close menu slot");
		    				sendLocalMessage(chest.inventorySlots.getInventory().get(49).getItem().getRegistryName());
		    				gameState = gameState.DISABLED;
		    			}
		    		}
	    		}.start();
			} else {
				sendLocalMessage("Unexpected chest size for state COMMANDSENT, disabling mod");
				gameState = gameState.DISABLED;
			}
		} else if (gameState == gameState.CONTINUEFIRSTWINDOW) {
			if (chest.inventorySlots.inventorySlots.size() == 27 + 36) {
				//Assume that we found the right chest. 
				sendLocalMessage("Found Confirm Window");
				sendExpireTime = System.currentTimeMillis() + 1000;
				gameState = gameState.SECONDWINDOW;
				//Spin up a thread to handle parsing the window
				new Thread() {
	    			@Override
	    			public void run() {
	    				while (Objects.isNull(chest.inventorySlots.getInventory().get(11)) && !chest.inventorySlots.getInventory().get(11).getItem().getRegistryName().equals("minecraft:stained_hardened_clay")) {
		    				sendLocalMessage("Waiting...");
		    				try {
								Thread.sleep(20);
							} catch (InterruptedException e) {
								e.printStackTrace();
								sendLocalMessage("Thread interrupted while sleeping, disabling mod");
								gameState = gameState.DISABLED;
								return;
							}
		    			}
	    		    	sendExpireTime = System.currentTimeMillis() + 1000;
	    		    	gameState = gameState.CONTINUESECONDWINDOW;
	    			}
	    		}.start();
			}
		}
	}
	
	@SubscribeEvent
    public void handleCommands(CommandEvent event) {
		if (event.command.getCommandName() == "toggleModEnable") {
			if(gameState == gameState.DISABLED) {
				sendLocalMessage("Going into Enable State");
				gameState = gameState.ONSERVER;
			} else {
				sendLocalMessage("Going into Disable State");
				gameState = gameState.DISABLED;
			}
		} else if (event.command.getCommandName() == "getState") {
			sendLocalMessage("Current mod state is " + gameState.toString());
		}
	}
	
	@SubscribeEvent
	public void handleChatMessages(ClientChatReceivedEvent event) {
		if (gameState == gameState.COMMANDSENT) {
			if (event.message.getFormattedText().contains("This auction wasn't found!")) {
    			sendLocalMessage("Auction Already Deleted");
    			gameState = gameState.ONSERVER;
    		}
		}
	}
	
	private void getNetHandler() {
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
			sendLocalMessage("Failed to get field name of nethandler");
			gameState = gameState.DISABLED;
			return;
		}
		
		// get net handler
		try {
			clientHandler = PlayerControllerMP.class.getDeclaredField(fieldName);
		} catch (Exception e) {
			sendLocalMessage("Failed to get clienthandler field");
			e.printStackTrace();
			gameState = gameState.DISABLED;
			return;
		}
		
		// set it to accessible and get its active instance
		clientHandler.setAccessible(true);
    	try {
    		PlayerControllerMP pc = Minecraft.getMinecraft().playerController;
			netHandler = (NetHandlerPlayClient) clientHandler.get(pc);
			sendLocalMessage("Grabbed Handler");
		} catch (Exception e) {
			sendLocalMessage("Failed to grab handler");
			gameState = gameState.DISABLED;
		}
	}
	
	private GameStateEnum getLocation() {
		String location;
		ScorePlayerTeam t;
		try {
			Scoreboard s = Minecraft.getMinecraft().thePlayer.getWorldScoreboard();
			t = s.getTeams().stream().filter(new Predicate<ScorePlayerTeam>() {
				@Override
				public boolean test(ScorePlayerTeam team) {
					if (team.getColorPrefix().length() > 4 && team.getColorPrefix().charAt(3) == (char)9187) {
						return true;
					}
					return false;
				}
			}).findFirst().orElse(null);
		} catch (Exception e) {
			sendLocalMessage("Error resolving scoreboard");
			return gameState.DISABLED;
		}
		if (t == null) {
			sendLocalMessage("Location row not found");
			return gameState.DISABLED;
		}
		
		location = t.getColorPrefix().substring(7);
		if(t.getColorSuffix() != null && !t.getColorSuffix().isEmpty()) {
			location += t.getColorSuffix().substring(2);
		}
		if ("Auction House".equals(location)) {
			return gameState.AUCTIONHOUSE;
		} else if ("Village".equals(location)) {
			return gameState.HUB;
		} else {
			return gameState.ONSERVER;
		}
		
		
	}
	
	private void checkServerStatus() {
		if (Objects.isNull(Minecraft.getMinecraft().getCurrentServerData())) {
			gameState = gameState.DISABLED;
		}
	}
	
	private void checkFile() {
		try {
    		// Check that the file has data and we aren't currently trying to purchase another item
    		if (ipcFile.length() != 0) {
    			// if it does, read it
    			try {
					ipcScanner = new Scanner(ipcFile);
				} catch (FileNotFoundException e) {
					sendLocalMessage("Trouble reading the file, file not found");
					gameState = gameState.DISABLED;
					return;
				}
    			ipcData = ipcScanner.nextLine();
    			ipcScanner.close();
    			try {
					ipcFlusher = new FileWriter(ipcFile, false);
				} catch (IOException e) {
					sendLocalMessage("Trouble deleting the file, file not found");
					gameState = gameState.DISABLED;
					return;
				}
    			try {
    				ipcFlusher.flush();
        			ipcFlusher.close();
    			} catch (IOException e) {
    				sendLocalMessage("Trouble clearing the file");
    				gameState = gameState.DISABLED;
					return;
    			}
    			
    			split = ipcData.indexOf(",");
    			System.out.println(split);
    			uuid = ipcData.substring(0, split);
    			nextSendTime = Long.valueOf(ipcData.substring(split + 1));
    			gameState = gameState.COMMANDREADY;
    			sendLocalMessage("Data Received");
    			
    		}
		} catch (Exception e) {
    		e.printStackTrace();
    		sendLocalMessage("Unknown error!");
    		gameState = gameState.DISABLED;
    	}
	}
	
	private void sendLocalMessage(String s) {
		Minecraft.getMinecraft().thePlayer.addChatMessage(new ChatComponentText(s));
	}
	
	private void sendChestClickPacket(int windowId, int slotNumber, ItemStack itemStack) {
		netHandler.addToSendQueue(new C0EPacketClickWindow(windowId, slotNumber, 0, 0, itemStack, (short)1));
	}
	
	private void printGameState() {
		//TODO find some way to display game state
		return;
	}
}
