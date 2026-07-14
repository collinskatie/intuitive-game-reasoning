import React from "react";
import {
  usePlayer,
  usePlayers,
  useRound,
  Slider,
} from "@empirica/core/player/classic/react";
import { Button } from "../components/Button";
import "../../node_modules/@empirica/core/dist/player-classic-react.css";
import { useState, useEffect } from "react";
import { THINKING_TIME_RESPOND } from "../Constants.jsx";

export function Judge() {
  const player = usePlayer();
  const players = usePlayers();
  const round = useRound();
  const partner = players.filter((p) => p.id !== player.id)[0];

  const stimID = round.get("stimuliID");
  var numRows = round.get("numRows");
  var numCols = round.get("numCols");
  const winConds = round.get("winConds");
  const gameMetaData = round.get("stimuliMetaData");

  player.round.set("stimuliID", stimID);

  var CELL_SIZE = 40; 
  if (numRows >= 9 && numCols >= 9){
    CELL_SIZE = 25;
  } 
  else if (numRows >= 7 && numCols >= 7){
    CELL_SIZE = 30;
  } 

  const buttonStyle = {
    width: CELL_SIZE,
    height: CELL_SIZE,
    itemsAlign: "center",
    backgroundColor: "white",
    color: "white",
    fontWeight: "bold",
    border: "1px solid black",
    fontSize: "24px",
    display: "inline-block",
  };

  const visitStylePlayer1 = {
    width: CELL_SIZE,
    height: CELL_SIZE,
    itemsAlign: "center",
    backgroundColor: "blue",
    color: "blue",
    fontWeight: "bold",
    border: "1px solid black",
    fontSize: "24px",
    display: "inline-block",
  };

  const visitStylePlayer2 = {
    width: CELL_SIZE,
    height: CELL_SIZE,
    itemsAlign: "center",
    backgroundColor: "red",
    color: "red",
    fontWeight: "bold",
    border: "1px solid black",
    fontSize: "24px",
    display: "inline-block",
  };

  const allBoards = round.get("allBoards");
  var board = allBoards[allBoards.length-1];
  const judgmentTask = round.get("judgmentTask");
  const [showButton, setShowButton] = useState(false);

  console.log("all boards: ", allBoards)

  if (board == undefined) {
    // somehow the game ended before a move was made
    // take the 'empty' initial board
    board = round.get("board") 
  }

  const [sliderMoved, setSliderMoved] = useState({
    judgment: false,
    judgmentSkill: false,
    judgmentAdvantage: false,
    judgmentDraw: false
  });

  useEffect(() => {
    const timer = setTimeout(() => {
      setShowButton(true);
      document.getElementById("slider-container")?.scrollIntoView({ behavior: "smooth" });
    }, THINKING_TIME_RESPOND * 1000);

    return () => clearTimeout(timer);
  }, []);

  function handleChange(e) {
    var newValue = e.target.valueAsNumber;
    player.round.set("judgment", newValue);
    setSliderMoved(prev => ({ ...prev, judgment: true }));
  }

  function handleChangeAdvantage(e) {
    var newValue = e.target.valueAsNumber;
    player.round.set("judgmentAdvantage", newValue);
    setSliderMoved(prev => ({ ...prev, judgmentAdvantage: true }));
  }

  function handleChangeDraw(e) {
    var newValue = e.target.valueAsNumber;
    player.round.set("judgmentDraw", newValue);
    setSliderMoved(prev => ({ ...prev, judgmentDraw: true }));
  }

  function handleChangeSkill(e) {
    var newValue = e.target.valueAsNumber;
    player.round.set("judgmentSkill", newValue);
    setSliderMoved(prev => ({ ...prev, judgmentSkill: true }));
  }

  // Determine if all required sliders have been moved based on judgment task
  const areAllSlidersMoved = () => {
    if (judgmentTask === "how_fun") {
      return sliderMoved.judgment && sliderMoved.judgmentSkill;
    } else if (judgmentTask === "advantage") {
      return sliderMoved.judgmentAdvantage && 
             sliderMoved.judgmentDraw && 
             sliderMoved.judgmentSkill;
    }
    return false;
  };

  // Modify the submit button to be disabled until all sliders are moved
  const handleSubmit = () => {
    if (areAllSlidersMoved()) {
      player.stage.set("submit", true);
    }
  };


  const funSliderLabels = [
    "The least fun of this class<br></br>of grid-based game",
    "Neutral",
    "The most fun of this class<br></br>of grid-based game",
  ];

  const advantageSliderLabels = [
    "First player<br></br>definitely going to <strong>lose</strong>",
    "Equally likely to<br></br><strong>win or lose</strong>",
    "First player<br></br>definitely going to <strong>win</strong>",
  ];

  const drawSliderLabels = [
    "Impossible to<br></br>end in a draw",
    "Equally likely to<br></br>end in a draw or not",
    "Definitely going to<br></br>end in a draw",
  ];

  const skillSliderLabels = [
    "Better than 0<br></br>other players", // <br></br>(this player isn't better<br></br>than any other player)",
    "Better than 50<br></br>other players", // 50 <br></br>(this player is about as good <br></br>as the average player)",
    "Better than all 100<br></br>other players", //"100 <br></br>(this player is better<br></br>than every other player)"
  ];

  return (
    <div className="flex flex-col min-h-screen">
      {/* Header section - Always visible with reduced margin */}
      {/* <div className="w-full bg-white py-2 px-4 sticky top-0 z-10"> */}
      <div className="w-full bg-white py-2 px-4 sticky top-0 z-10">
      {!showButton && <div>
      <p className="text-center text-md font-medium">
          You must think for at least <strong>{THINKING_TIME_RESPOND} seconds</strong> about the following questions before responding.
          </p>

          <p className="text-center text-md font-medium">The response sliders will appear after {THINKING_TIME_RESPOND} seconds have passed. 
          </p>
          <br></br>
          </div>
      }
        <p className="text-center text-md font-medium">
          Games take place on a <strong> {numRows} x {numCols} board. 
          </strong>
         <br></br>The rules for this game are: <strong>{winConds}</strong>
         <br></br>Now remember, the following questions are <i>not about the particular match you played</i> but <strong>this game overall, with these rules</strong> for two new reasonable human players (and an assessment of your opponent against new players).
        </p>
      </div>

      {/* Game board section with reduced margin */}
      <div className="flex justify-center sticky my-2">
        <div className="grid">
          {board.map((arr, rowIndex) => (
            <div key={rowIndex} className="flex justify-center">
              {arr.map((cell, colIndex) => {
                let moveNumber = null;
                allBoards.forEach((currentBoard, moveIndex) => {
                  if (
                    currentBoard[rowIndex][colIndex] !== 0 &&
                    (moveIndex === 0 || allBoards[moveIndex - 1][rowIndex][colIndex] === 0)
                  ) {
                    moveNumber = moveIndex + 1;
                  }
                });

                return (
                  <div
                    key={`${rowIndex}-${colIndex}`}
                    style={{
                      position: "relative",
                      ...(
                        cell === 0
                          ? buttonStyle
                          : cell === 1
                          ? visitStylePlayer1
                          : visitStylePlayer2
                      ),
                    }}
                  >
                    {moveNumber && (
                      <span className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-white font-bold text-sm">
                        {moveNumber}
                      </span>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>

      <br></br>

{judgmentTask === "how_fun" && (
  <>
    <p style={{ textAlign: "center" }}>
    <strong><u>Question 1: </u>How fun is this game?</strong>
    </p>
    <br />
    <br />
    {showButton &&
    <div
      style={{
        margin: "20px 0",
        width: "80%",
        marginLeft: "auto",
        marginRight: "auto",
      }}
    >
      <Slider
        value={player.round.get("judgment")}
        onChange={handleChange}
        max={100}
        step={1}
      />
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          flexWrap: "wrap",
          textAlign: "center",
        }}
      >
        {funSliderLabels.map((label, index) => (
          <span
          key={index}
          style={{
            flex: "0 0 auto", // Prevent stretching
            minWidth: "0", // Ensure no overflow
            textAlign: index === 0 ? "left" : index === funSliderLabels.length - 1 ? "right" : "center", // Align endpoints properly
            lineHeight: "1.2", // Adjust for spacing if needed
          }}
          dangerouslySetInnerHTML={{ __html: label }}
        ></span>
        ))}
      </div>
    </div>}
    <br></br>
    <p style={{ textAlign: "center" }}>
    <strong><u>Question 2: </u> Out of 100 other random new players, where do you think the opponent you just played would rank in skill for this game?<br></br></strong>
    </p>
    <br />
    <br />
    {showButton &&
    <div
      style={{
        margin: "20px 0",
        width: "80%",
        marginLeft: "auto",
        marginRight: "auto",
      }}
    >
      <Slider
        value={player.round.get("judgmentSkill")}
        onChange={handleChangeSkill}
        max={100}
        step={1}
      />
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          flexWrap: "wrap",
          textAlign: "center",
        }}
      >
        {skillSliderLabels.map((label, index) => (
          <span
          key={index}
          style={{
            flex: "0 0 auto", // Prevent stretching
            minWidth: "0", // Ensure no overflow
            textAlign: index === 0 ? "left" : index === skillSliderLabels.length - 1 ? "right" : "center", // Align endpoints properly
            lineHeight: "1.2", // Adjust for spacing if needed
          }}
          dangerouslySetInnerHTML={{ __html: label }}
        ></span>
        ))}
      </div>
    </div>}
  </>
)}

{judgmentTask === "advantage" && (
  <>
    <p style={{ textAlign: "center" }}>
    <strong><u>Question 1: </u>
      Assuming <i>two NEW random human players</i> play reasonably, if the game <i>does not end in a draw</i>, how likely is it that the first player is going to win (<i>not draw</i>)?
      </strong>
    </p>
    <br />
    <br />
    {showButton &&
    <div
      style={{
        margin: "20px 0",
        width: "80%",
        marginLeft: "auto",
        marginRight: "auto",
      }}
    >
      <Slider
        value={player.round.get("judgmentAdvantage")}
        onChange={handleChangeAdvantage}
        max={100}
        step={1}
      />
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          flexWrap: "wrap",
          textAlign: "center",
        }}
      >
        {advantageSliderLabels.map((label, index) => (
          <span
          key={index}
          style={{
            flex: "0 0 auto", // Prevent stretching
            minWidth: "0", // Ensure no overflow
            textAlign: index === 0 ? "left" : index === advantageSliderLabels.length - 1 ? "right" : "center", // Align endpoints properly
            lineHeight: "1.2", // Adjust for spacing if needed
          }}
          dangerouslySetInnerHTML={{ __html: label }}
        ></span>
        ))}
      </div>
    </div>}
    <br></br>
    <p style={{ textAlign: "center" }}>
    <strong><u>Question 2: </u> Assuming both new human players play reasonably, how likely is the game to end in a draw?</strong>
    </p>
    <br />
    <br />
    {showButton &&
    <div
      style={{
        margin: "20px 0",
        width: "80%",
        marginLeft: "auto",
        marginRight: "auto",
      }}
    >
      <Slider
        value={player.round.get("judgmentDraw")}
        onChange={handleChangeDraw}
        max={100}
        step={1}
      />
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          flexWrap: "wrap",
          textAlign: "center",
        }}
      >
        {drawSliderLabels.map((label, index) => (
          <span
          key={index}
          style={{
            flex: "0 0 auto", // Prevent stretching
            minWidth: "0", // Ensure no overflow
            textAlign: index === 0 ? "left" : index === drawSliderLabels.length - 1 ? "right" : "center", // Align endpoints properly
            lineHeight: "1.2", // Adjust for spacing if needed
          }}
          dangerouslySetInnerHTML={{ __html: label }}
        ></span>
        ))}
      </div>
    </div>}
    <br></br>
    <p style={{ textAlign: "center" }}>
      <strong><u>Question 3: </u> Out of 100 other random new players, where do you think the opponent you just played would rank in skill for this game?<br></br></strong>
    </p>
    <br />
    <br />
    {showButton && (
<div
style={{
margin: "20px 0",
width: "80%",
marginLeft: "auto",
marginRight: "auto",
}}
>
<Slider
value={player.round.get("judgmentSkill")}
onChange={handleChangeSkill}
max={100}
step={1}
/>
<div
style={{
  display: "flex",
  justifyContent: "space-between", // Space evenly between endpoints
  textAlign: "center",
}}
>
{skillSliderLabels.map((label, index) => (
  <span
    key={index}
    style={{
      flex: "0 0 auto", // Prevent stretching
      minWidth: "0", // Ensure no overflow
      textAlign: index === 0 ? "left" : index === skillSliderLabels.length - 1 ? "right" : "center", // Align endpoints properly
      lineHeight: "1.2", // Adjust for spacing if needed
    }}
    dangerouslySetInnerHTML={{ __html: label }}
  ></span>
))}
</div>
</div>
)}
  </>
)}

{showButton &&
        <div style={{ textAlign: "center" }}>
          <Button 
            handleClick={handleSubmit} 
            disabled={!areAllSlidersMoved()}
          >
            Submit Response
          </Button>
          {!areAllSlidersMoved() && (
            <p style={{ color: 'red', marginTop: '10px' }}>
              Please move all sliders before submitting
            </p>
          )}
        </div>
      }
</div>
);
}

export default Judge;