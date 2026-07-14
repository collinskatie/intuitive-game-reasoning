import React from "react";
import { Button } from "../components/Button";
import { THINKING_TIME, TOTAL_TIME, BASE_RATE, GAME_COUNT, BONUS, THINKING_TIME_RESPOND } from "../Constants.jsx";
import { usePlayer } from "@empirica/core/player/classic/react";
import { useState, useEffect } from "react";

export function Introduction({ next }) {
  return (
    <div className="mt-3 sm:mt-5 p-20">
      <h3 className="text-lg leading-6 font-medium text-gray-900">
        Instructions
      </h3>
      <div className="mt-2 mb-6">
        <p>Welcome! </p>{" "}
        <p>
          {" "}
          We are conducting an experiment to understand how people think about
          games.
        </p>
      </div>
      <Button handleClick={next} autoFocus>
        <p>Next</p>
      </Button>
    </div>
  );
}

export function IntroductionPay({ next }) {
  return (
    <div className="mt-3 sm:mt-5 p-20">
      <h3 className="text-lg leading-6 font-medium text-gray-900">
        Instructions
      </h3>
      <div className="mt-2 mb-6">
        <p>We take your time and compensation seriously.</p>
        <br></br>
        <p>
          We expect that the experiment will take <strong>{TOTAL_TIME}</strong> minutes. You
          will be paid at a base rate of <strong>{BASE_RATE}</strong> per hour.
        </p>
        <br></br>
        <p>If any issues arise, please contact katiemc@mit.edu.</p>
      </div>
      <Button handleClick={next} autoFocus>
        <p>Next</p>
      </Button>
    </div>
  );
}

export function Introduction2({ next }) {
  return (
    <div className="mt-3 sm:mt-5 p-20">
      <h3 className="text-lg leading-6 font-medium text-gray-900">
        Instructions
      </h3>
      <div className="mt-2 mb-6">
        <p>
          In this experiment, you will be playing a series of{" "}
          <strong>{GAME_COUNT} board games</strong> against another human player.
        </p>
        <br></br>
        <p>
          The other player will also be participating in the experiment live. At
          times, you may not be able to proceed to the next screen while you
          wait for your opponent to proceed.
        </p>
        <br></br>
        <p>
          If at any time your opponent stops the experiment, the experiment will
          end. You will still be componensated for your time.
        </p>
      </div>
      <Button handleClick={next} autoFocus>
        <p>Next</p>
      </Button>
    </div>
  );
}

export function Introduction3({ next }) {
  return (
    <div className="mt-3 sm:mt-5 p-20">
      <h3 className="text-lg leading-6 font-medium text-gray-900">
        Instructions
      </h3>


      <div className="mt-2 mb-6">
        <p>
          Before you begin to play, please <strong>carefully read the game description, as the games are played on boards of different sizes and with different rules for winning.</strong>
        </p>
        <br></br>
        <p>
          You will be <strong>randomly assigned to play first or second</strong>{" "}
          for each game.
        </p>
        <br></br>

        <p> 
          The board will turn grey when it is not your turn. 
        </p><br></br>


        {/* <p>
          You will have <strong>10 seconds</strong> to make a move. If you do
          not make a move within the time limit, the game will automatically
          make a <i>random</i> move for you.
        </p>
        <br></br> */}

        {/* <p>
        You may <strong>request a draw</strong> at any point during a game by pressing the <strong>"Request a Draw"</strong> button.
        However, your opponent can reject the request (and you can also reject such a draw request to keep playing).
        If both players accept the draw, the game will end.
        </p>
        <br></br>
        <p>Please be <strong>respectful</strong> for the other player; if you request a draw several times and they keep declining, please do not keep requesting a draw.</p> */}

        
      </div>
      <Button handleClick={next} autoFocus>
        <p>Next</p>
      </Button>
    </div>
  );
}

export function Introduction3Buttons({ next }) {
  return (
    <div className="mt-3 sm:mt-5 p-20">
      <h3 className="text-lg leading-6 font-medium text-gray-900">
        Instructions
      </h3>


      <div className="mt-2 mb-6">
        <p>
          If you are certain you will lose, you may <strong>surrender</strong> by pressing the <strong>"Surrender"</strong> button. 
          <br></br>
          <br></br>
          You will immediately lose and the game will end if you surrender. 
        </p>
        <br></br>

        <p>At any point in the game, you may also <strong>request a draw</strong> by pressing the <strong>"Request a Draw"</strong> button.
        
        <br></br>
        <br></br>
        However, <strong>your opponent can reject the request</strong> (and <strong>you can also reject any draw request made by your opponent</strong> to keep playing).
        If both players accept the draw, the game will end.
        </p>
        <br></br>
        <p>Please be <strong>respectful</strong> for the other player; if you request a draw several times and they keep declining, please do not keep requesting a draw.</p>

        
      </div>
      <Button handleClick={next} autoFocus>
        <p>Next</p>
      </Button>
    </div>
  );
}



export function Introduction4({ next }) {
  return (
    <div className="mt-3 sm:mt-5 p-20">
      <h3 className="text-lg leading-6 font-medium text-gray-900">
        Instructions
      </h3>
      <div className="mt-2 mb-6">
      <p>
          <br></br>Some of these games are easier or harder to win than others. Please <strong>try your best</strong> in each game. You will get a{" "}
          <strong>bonus of {BONUS} per game that you win!</strong> You will not receive a bonus for a loss or draw.
        </p>
        <br></br>
        <p>
          After each match, you will be shown the match that you just played, and <strong>you will answer simple questions about the match</strong>, e.g., the predicted skill of the other player, <strong>and the game as a whole</strong> by dragging a slider.
        </p>
        <br></br>
        <br></br>
      </div>
      <Button handleClick={next} autoFocus>
        <p>Next</p>
      </Button>
    </div>
  );
}

export function Introduction4b({ next }) {
  return (
    <div className="mt-3 sm:mt-5 p-20">
      <h3 className="text-lg leading-6 font-medium text-gray-900">
        Instructions
      </h3>
      <div className="mt-2 mb-6">
      <p>
        For instance, if we ask you about how fun this game is, we are asking you how fun you think it would be to play this game in general <i>against a random new player.</i></p>
        <br></br>
        <p>Similarly, if we ask you how likely it is that the first player would win, we are asking you to gauge how likely it would be <i>against a random new player</i>. You should treat your experience with your particular opponent as only an example of how the game works.
        </p> 
        <br></br>
        <p>We emphasize these questions are <i>not</i> about the match that you just played, but <strong>this game overall</strong> with the specific rules (and any two new reasonable human players).</p>
        <br></br>

        <p>You will have to spend at least <strong>{THINKING_TIME_RESPOND} seconds</strong> before you can respond.</p>

        <br></br>
        <br></br>
      </div>
      <Button handleClick={next} autoFocus>
        <p>Next</p>
      </Button>
    </div>
  );
}

export function Introduction4c({ next }) {
  return (
    <div className="mt-3 sm:mt-5 p-20">
      <h3 className="text-lg leading-6 font-medium text-gray-900">
        Instructions
      </h3>
      <div className="mt-2 mb-6">
        <p>
          NOTE: depending on your browser, the sliders may snap back and forth. Please <strong>make sure the value at the slider matches what you intend</strong> before submitting!
        </p>
        <br></br>
        <p>
       We recommend <strong>clicking</strong> along the slider (rather than dragging).
        </p>
        <br></br>
        <br></br>
      </div>
      <Button handleClick={next} autoFocus>
        <p>Next</p>
      </Button>
    </div>
  );
}

export function Introduction5({ next }) {
  return (
    <div className="mt-3 sm:mt-5 p-20">
      <h3 className="text-lg leading-6 font-medium text-gray-900">
        Instructions
      </h3>
      <div className="mt-2 mb-6">
        <p>
          We will show you the description of each game before you begin playing. 
        </p>
        <br></br>
        <p>
        To make sure that you understand the rules of the game, you must spend at least <strong>{THINKING_TIME} seconds</strong> reading before you will be able to play.
        </p>
        <br></br>
        <p>
          The CONTINUE button will appear when the time has completed (but you are welcome to take longer before starting). 
        </p>
        <br></br>
      </div>
      <Button handleClick={next} autoFocus>
        <p>Next</p>
      </Button>
    </div>
  );
}

export function ComprehensionCheck({ next }) {
  
  
  const player = usePlayer();

  // this function gets called when any of the contribution buttons are clicked.
  var anyIncorrect = false
  var clicked1 = false
  var clicked2 = false 
  var clicked3 = false
  var clicked1_option = ''
  var clicked2_option= ''
  var clicked3_option = ''
  console.log('any incorrect?', anyIncorrect)
  
  function onClick(option) {
    console.log("Player Pressed Button: ", option);
    // if (option == "B"){
    //   anyIncorrect = true
    //   console.log('incorrect 1', anyIncorrect)
    // }
    clicked1_option = option
    clicked1 = true

    // if (anyIncorrect){ 
    //   console.log("failed check...")
    //   player.set("intro", 1)
    // }
    // // else {
    // //   console.log("passed check!")
    // //   // next();
    // // }
    
  }

  function onClick2(option) {
    console.log("Player Pressed Button: ", option);
    // if (option == "A"){
    //   anyIncorrect = true
    //   console.log('incorrect 2', anyIncorrect)
    // }
    clicked2_option = option
    clicked2 = true 
    
  }


  function onClick3(option) {
    console.log("Player Pressed Button: ", option);
    // if (option == "A"){
    //   console.log('incorrect 3', anyIncorrect)
    //   anyIncorrect = true
    // }

    clicked3_option = option

    clicked3 = true
    
  }
  function checkNext(){
    var anyIncorrect = false
    if ((clicked1_option != 'A') || (clicked2_option != 'B') || (clicked3_option != 'B')){
      anyIncorrect = true
    }

    if (anyIncorrect){ 
      console.log("failed check...")
      player.set("intro", 1)
    }
    else {
      console.log("passed check!")
      if (clicked1 && clicked2 && clicked3){ 
        next();
      }
    }
  }
  
  return (
    <div className="mt-3 sm:mt-5 p-20">
      <h3 className="text-lg leading-6 font-medium text-gray-900">
        Understanding Check
      </h3>
      
      <div className="mt-2 mb-6">
        <p>
          Before you start, please answer a brief understanding check. If you do not get the answers correct, you will be taken back to the start of the instructions.
        </p>
        <br></br>
        <div>
                <p>Question 1: How will you know it's not your turn?</p>
                <br></br>
                <label>
                    <input type="radio" name="question1" value="optionA" onChange={() => onClick('A')} /> The board will be grey.
                </label>
                <br></br>
                <label>
                    <input type="radio" name="question1" value="optionB" onChange={() => onClick('B')} /> The board will be beep.
                </label>
            </div>
            <br></br>

            <div>
                <p>Question 2: What happens if your opponent requests a draw?</p>
                <br></br>
                <label>
                    <input type="radio" name="question2" value="optionA" onChange={() => onClick2('A')} /> The game will end immediately.
                </label>
                <br></br>
                <label>
                    <input type="radio" name="question2" value="optionB" onChange={() => onClick2('B')} /> You will be given the option to accept or reject it.
                </label>
            </div>
            <br></br>

            <div>
                <p>Question 3: What will you be doing after each game?</p>
                <br></br>
                <label>
                    <input type="radio" name="question3" value="optionA" onChange={() => onClick3('A')} /> Writing a summary of your strategy.
                </label>
                <br></br>
                <label>
                    <input type="radio" name="question3" value="optionB" onChange={() => onClick3('B')} /> Answering one or more questions about the game via a slider.
                </label>
            </div>
      </div>

      <Button handleClick={() => checkNext()} autoFocus>
        <p>Next</p>
      </Button> 
    </div>
  );
}


export function ConsentForm({ next }) {
  
  
  const player = usePlayer();

  // State to manage checkboxes
  const [ageChecked, setAgeChecked] = useState(false);
  const [readChecked, setReadChecked] = useState(false);
  const [consentChecked, setConsentChecked] = useState(false);

  // this function gets called when the "Start Experiment" button is clicked.
  function onClick() {
    if (ageChecked && readChecked && consentChecked) {
      console.log("All checkboxes checked. Proceeding...");
      next();
    } else {
      console.log("Not all checkboxes are checked. Can't proceed.");
      player.set("intro", 0);
    }
  }
  
  return (
    <div className="mt-3 sm:mt-5 p-20">
      <h3 className="text-lg leading-6 font-medium text-gray-900">
        Consent Form
      </h3>

      <br></br>
      <h2 align="center"><strong>Welcome to our study!</strong></h2>
  <p>
    By completing this study, you are participating in a study being performed by researchers from MIT, Princeton, and the University of Cambridge. The purpose of this research is to study human reasoning about games, and the results will inform cognitive science and AI research.
  </p>
  <br></br>
  <p> You must be at least 18 years old to participate. There are neither specific benefits nor anticipated risks associated with participation in this study. Your participation in this study is completely voluntary and you can withdraw at any time by simply exiting the study. You may decline to answer any or all of the following questions. Choosing not to participate or withdrawing will result in no penalty. Your anonymity is assured; the researchers who have requested your participation will not receive any personal information about you, and any information you provide will not be shared in association with any personally identifying information.
  </p>
  <br></br>
  <p>
If you have questions about this research, please contact the researchers by sending an email to katiemc@mit.edu. These researchers will do their best to communicate with you in a timely, professional, and courteous manner. If you have questions regarding your rights as a participant, or if problems arise which you do not feel you can discuss with the researchers, please contact the Computational Cognitive Science Group at MIT.
  </p>
  <br></br>
<p>
Your participation in this research is voluntary. You may discontinue participation at any time during the research activity. You may print a copy of this consent form for your records.
    </p>
    <br></br>
  <p>
    To continue, check the checkboxes below and click "Start Experiment".
  </p>
  <br></br>
  <p>
        <input
          type="checkbox"
          id="age_checkbox"
          onChange={(e) => setAgeChecked(e.target.checked)}
        />
        I am age 18 or older
      </p>
      <br></br>
      <p>
        <input
          type="checkbox"
          id="read_checkbox"
          onChange={(e) => setReadChecked(e.target.checked)}
        />
        I have read and understand the information above.
      </p>
      <br></br>
      <p>
        <input
          type="checkbox"
          id="consent_checkbox"
          onChange={(e) => setConsentChecked(e.target.checked)}
        />
        I want to participate in this research and continue with the experiment.
      </p>
      <br></br>
      <button onClick={onClick}>Start Experiment</button>
    </div>
  );
}