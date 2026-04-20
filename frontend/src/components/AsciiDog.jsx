const ASCII = {
  scared: "            __\n      (___()';;\n      /,    /'\n      \\\\--\\\\",
  cautious: "            __\n      (___()'`;\n      /,    /'\n      \\\\--\\\\",
  curious: "            __\n      (___()'?\n      /,    /'\n      \\\\--\\\\",
  happy: "            __\n      (___()'`;\n      /,  ^  /'\n      \\\\--\\\\",
  thriving: "            __\n      (___()'`;\n      /,  ^  /'\n      \\\\~~\\\\",
  sad: "            __\n      (___()'.;\n      /,    /'\n      \\\\--\\\\",
  sick: "            __\n      (___()'x;\n      /,    /'\n      \\\\--\\\\",
};

export default function AsciiDog({ mood = 'scared', chatBubble = null }) {
  const art = ASCII[mood] || ASCII.scared

  return (
    <div className="ascii-dog-container">
      {chatBubble && (
        <div className="chat-bubble">{chatBubble}</div>
      )}
      <pre className="ascii-dog">{art}</pre>
    </div>
  )
}
