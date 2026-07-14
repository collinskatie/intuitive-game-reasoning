import { EmpiricaClassic } from "@empirica/core/player/classic";
import { EmpiricaContext } from "@empirica/core/player/classic/react";
import { EmpiricaMenu, EmpiricaParticipant } from "@empirica/core/player/react";
import React from "react";
import { Game } from "./Game";
import { ExitSurvey } from "./intro-exit/ExitSurvey";
import {Sorry} from "./intro-exit/Sorry";
import { ConsentForm, Introduction, IntroductionPay, Introduction2, Introduction3, Introduction3Buttons, Introduction4, Introduction4b, Introduction4c, Introduction5, ComprehensionCheck } from "./intro-exit/Introduction";

var debugMode = false

export default function App() {
  const urlParams = new URLSearchParams(window.location.search);
  const playerKey = urlParams.get("participantKey") || "";

  const { protocol, host } = window.location;
  const url = `${protocol}//${host}/query`;

  function introSteps({ game, player }) {
    if (debugMode) {
      return [Introduction]
    }
    else {
     return [ConsentForm, Introduction, IntroductionPay, Introduction2, Introduction3, Introduction3Buttons, Introduction4, Introduction4b, Introduction4c, Introduction5, ComprehensionCheck]
    }
    
  }

  function exitSteps({ game, player }) {
    if (player.get("ended") == "game ended" || player.get("ended") == "game terminated") {
      return [ExitSurvey];
    }
    else{
      return [Sorry];
    }
  }

  return (
    <EmpiricaParticipant url={url} ns={playerKey} modeFunc={EmpiricaClassic}>
      <div className="h-screen relative">
        <EmpiricaMenu position="bottom-left" />
        <div className="h-full overflow-auto">
          <EmpiricaContext introSteps={introSteps} exitSteps={exitSteps}>
            <Game />
          </EmpiricaContext>
        </div>
      </div>
    </EmpiricaParticipant>
  );
}
