package com.example.examplemod;

import net.minecraft.command.CommandBase;
import net.minecraft.command.CommandException;
import net.minecraft.command.ICommandSender;

public class ResetModCommand extends CommandBase{

	@Override
	public String getCommandName() {
		return "resetState";
	}

	@Override
	public String getCommandUsage(ICommandSender sender) {
		return "meow";
	}

	@Override
	public void processCommand(ICommandSender sender, String[] args) throws CommandException {
		System.out.println("Command run");
		//Minecraft.getDebugFPS()
	}
	
	@Override
	public int getRequiredPermissionLevel() {
		return 0;
	}
	 

}

