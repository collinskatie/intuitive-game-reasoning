import React from "react";
import { Button } from "../components/Button";
import { THINKING_TIME, TOTAL_TIME, BASE_RATE, GAME_COUNT, BONUS, THINKING_TIME_RESPOND } from "../Constants.jsx";
import { usePlayer } from "@empirica/core/player/classic/react";
import { useState, useEffect } from "react";
export function Sorry({ next }) {
  return (
    <div className="mt-3 sm:mt-5 p-20">
      <h3 className="text-lg leading-6 font-medium text-gray-900">
        Sorry
      </h3>
      <div className="mt-2 mb-6">
        <p>
          We apologize, it appears that there was an error or you were not paired with a player to play against.
        </p>
        <br></br>
        <p>
          Please Return your study, and we will provide a small partial compensation. 
        </p>
        <br></br>
        <p>
          If you participated in more than one live game with another opponent before seeing these screen, please write to us on Prolific.
        </p>
      </div>
    </div>
  );
}