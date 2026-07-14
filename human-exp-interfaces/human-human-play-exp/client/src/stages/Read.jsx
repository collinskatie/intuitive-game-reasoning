import React from "react";
import { usePlayer, usePlayers, useRound } from "@empirica/core/player/classic/react";
import { Button } from "../components/Button";
import { useState, useEffect } from "react";
import { THINKING_TIME } from "../Constants.jsx";



export function Read() {

  console.log("read stage!")
  const player = usePlayer();
  const players = usePlayers();
  const round = useRound();
  const partner = players.filter((p) => p.id !== player.id)[0];
  var playerOrder = player.round.get("playerOrder")

  if (playerOrder === 1){
    var parsedPlayerOrder = "first"
  }else{ 
    var parsedPlayerOrder = "second"
  }
  console.log("player: ", player, " partner: ", partner, "order: ", playerOrder)
  
  const stimID = round.get("stimuliID")
  const numRows = round.get("numRows");
  const numCols = round.get("numCols");
  const winConds = round.get("winConds");
  console.log("stimuli ID: ", stimID, numRows, numCols, winConds)

  // State to control the visibility of the button
  const [showButton, setShowButton] = useState(false);

  // Use effect to delay showing the button
  useEffect(() => {
    const timer = setTimeout(() => {
      setShowButton(true);
    }, THINKING_TIME * 1000); 

    // Cleanup the timer if the component unmounts before the time is up
    return () => clearTimeout(timer);
  }, []);

  return (
    <div>
      <p><strong>In this game,</strong> you will play on a <strong>{numRows} x {numCols} board</strong>.</p>
      <br></br>
      <p>The rules for this game are: <br></br><strong>{winConds}</strong></p>
      <br></br>
      <p>You will play live against an opponent.</p>
      <br></br>
      <p> <strong>You will move {parsedPlayerOrder}.</strong></p>
      <br></br>

      {showButton && (
        <Button handleClick={() => player.stage.set("submit", true)}>
          I understand the rules, let's start the game!
        </Button>
      )}


    </div>
  );
}