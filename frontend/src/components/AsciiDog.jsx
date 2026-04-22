import scaredImg   from '../assets/scared.png'
import cautiousImg from '../assets/cautious.png'
import curiousImg  from '../assets/curious.png'
import happyImg    from '../assets/happy.png'
import thrivingImg from '../assets/thriving.png'
import sadImg      from '../assets/sad.png'
import sickImg     from '../assets/sick.png'

const IMAGES = {
  scared:   scaredImg,
  cautious: cautiousImg,
  curious:  curiousImg,
  happy:    happyImg,
  thriving: thrivingImg,
  sad:      sadImg,
  sick:     sickImg,
}

// const ASCII = {
//   scared: "            __\n      (___()';;\n      /,    /'\n      \\\\--\\\\",
//   cautious: "            __\n      (___()'`;\n      /,    /'\n      \\\\--\\\\",
//   curious: "            __\n      (___()'?\n      /,    /'\n      \\\\--\\\\",
//   happy: "            __\n      (___()'`;\n      /,  ^  /'\n      \\\\--\\\\",
//   thriving: "            __\n      (___()'`;\n      /,  ^  /'\n      \\\\~~\\\\",
//   sad: "            __\n      (___()'.;\n      /,    /'\n      \\\\--\\\\",
//   sick: "            __\n      (___()'x;\n      /,    /'\n      \\\\--\\\\",
// };

export default function AsciiDog({ mood = 'scared', chatBubble = null }) {
  const src = IMAGES[mood] || IMAGES.scared

  return (
    <div className="ascii-dog-container">
      {chatBubble && (
        <div className="chat-bubble">{chatBubble}</div>
      )}
      <img src={src} alt={mood} className="dog-img" />
    </div>
  )
}
