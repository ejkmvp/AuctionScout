package com.example.examplemod;

import java.lang.reflect.Field;

import net.minecraft.client.Minecraft;
import net.minecraft.client.multiplayer.PlayerControllerMP;
import net.minecraft.client.network.NetHandlerPlayClient;
import net.minecraft.init.Blocks;
import net.minecraftforge.client.ClientCommandHandler;
import net.minecraftforge.common.MinecraftForge;
import net.minecraftforge.fml.common.Mod;
import net.minecraftforge.fml.common.Mod.EventHandler;
import net.minecraftforge.fml.common.event.FMLInitializationEvent;

@Mod(modid = ExampleMod.MODID, version = ExampleMod.VERSION)
public class ExampleMod
{
    public static final String MODID = "examplemod";
    public static final String VERSION = "1.0";
    
    @EventHandler
    public void init(FMLInitializationEvent event)
    {
		// some example code
    	System.out.println("DIRT BLOCK >> "+Blocks.dirt.getUnlocalizedName());
    	//Minecraft.getMinecraft().playerController
    	
    	try {
			//NetHandlerPlayClient client = (NetHandlerPlayClient) clientHandler.get(Minecraft.getMinecraft().playerController);
			MinecraftForge.EVENT_BUS.register(new EventHandlers());
			ClientCommandHandler.instance.registerCommand(new ToggleModCommand());
			
		} catch (Exception e) {
			System.out.println("Error");
			e.printStackTrace();
		}
    	
    }
    
}
