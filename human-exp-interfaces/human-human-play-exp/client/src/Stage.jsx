import {
  usePlayer,
  usePlayers,
  useRound,
  useStage,
} from "@empirica/core/player/classic/react";
import { Loading } from "@empirica/core/player/react";
import React from "react";
import { Read } from "./stages/Read";
import { Play } from "./stages/Play";
import { Judge } from "./stages/Judge";

export function Stage() {
  const player = usePlayer();
  const players = usePlayers();
  const round = useRound();
  const stage = useStage();


  if (player.stage.get("submit")) {
    if (players.length === 1) {
      console.log("player len 1 ", players)
      return <Loading />;
    }

    return (
      <div className="text-center text-gray-400 pointer-events-none">
        Please wait for other player(s).
      </div>
    );
  }


  switch (stage.get("name")) {
    case "read":
      return <Read />;
    case "play":
      return <Play />;
    case "judge":
        return <Judge />;
    default:
      return <Loading />;
  }
}