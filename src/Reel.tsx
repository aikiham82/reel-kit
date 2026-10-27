import { loadFont as loadArchivo } from '@remotion/google-fonts/Archivo';
import { loadFont as loadOswald } from '@remotion/google-fonts/Oswald';
import { linearTiming, TransitionSeries } from '@remotion/transitions';
import { fade } from '@remotion/transitions/fade';
import { Fragment } from 'react';
import { AbsoluteFill, Audio, Img, interpolate, OffthreadVideo, Sequence, staticFile, useCurrentFrame } from 'remotion';

export const FPS = 30;
const CARD_FRAMES = 75;
const CARD_FADE = 8;
const DEFAULT_OUTRO_SECONDS = 3.5;
const DEFAULT_FADE_SECONDS = 0.5;
const LIGHT = '#F4F1EA';
const DARK = '#0B0B0C';

const { fontFamily: display } = loadOswald('normal', { weights: ['600'] });
const { fontFamily: sans } = loadArchivo('normal', { weights: ['500', '600'] });

export interface Clip {
  file: string;
  seconds: number;
}

export interface IntroCard {
  kicker?: string;
  title: string;
  sub?: string;
}

export interface Outro {
  image?: string;
  text?: string;
  url?: string;
  seconds?: number;
}

export interface ReelProps {
  clips: Clip[];
  transition?: 'cut' | 'fade';
  fadeSeconds?: number;
  clipVolume?: number;
  music?: { file: string; volume?: number };
  accent?: string;
  intro?: IntroCard[];
  outro?: Outro;
}

const toFrames = (seconds: number) => Math.round(seconds * FPS);

const fadeFrames = (props: ReelProps) => (props.transition === 'fade' ? toFrames(props.fadeSeconds ?? DEFAULT_FADE_SECONDS) : 0);

const sceneFrames = (props: ReelProps) => [
  ...props.clips.map((clip) => toFrames(clip.seconds)),
  ...(props.outro ? [toFrames(props.outro.seconds ?? DEFAULT_OUTRO_SECONDS)] : []),
];

export const totalFrames = (props: ReelProps) => {
  const scenes = sceneFrames(props);
  return scenes.reduce((sum, frames) => sum + frames, 0) - fadeFrames(props) * (scenes.length - 1);
};

const Card = ({ card, accent }: { card: IntroCard; accent: string }) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, CARD_FADE, CARD_FRAMES - CARD_FADE, CARD_FRAMES], [0, 1, 1, 0], { extrapolateRight: 'clamp' });
  const y = interpolate(frame, [0, CARD_FADE], [24, 0], { extrapolateRight: 'clamp' });
  return (
    <AbsoluteFill style={{ background: 'linear-gradient(rgba(11,11,12,0.9) 0%, rgba(11,11,12,0.7) 32%, transparent 52%)', opacity }}>
      <div style={{ position: 'absolute', top: 270, left: 80, right: 80, color: LIGHT, transform: `translateY(${y}px)` }}>
        {card.kicker && (
          <div style={{ fontFamily: sans, fontWeight: 600, fontSize: 34, letterSpacing: '0.22em', textTransform: 'uppercase', color: accent }}>{card.kicker}</div>
        )}
        <div style={{ fontFamily: display, fontWeight: 600, fontSize: card.title.length > 14 ? 110 : 150, lineHeight: 1, marginTop: 28, textTransform: 'uppercase' }}>
          {card.title}
        </div>
        {card.sub && <div style={{ fontFamily: sans, fontWeight: 500, fontSize: 44, marginTop: 20 }}>{card.sub}</div>}
      </div>
    </AbsoluteFill>
  );
};

const OutroScene = ({ outro, accent }: { outro: Outro; accent: string }) => (
  <AbsoluteFill style={{ background: DARK, justifyContent: 'center', alignItems: 'center', gap: 36, color: LIGHT, textAlign: 'center' }}>
    {outro.text && <div style={{ fontFamily: sans, fontWeight: 600, fontSize: 34, letterSpacing: '0.22em', textTransform: 'uppercase', color: accent }}>{outro.text}</div>}
    {outro.url && <div style={{ fontFamily: sans, fontWeight: 500, fontSize: 38 }}>{outro.url}</div>}
    {outro.image && <Img src={staticFile(outro.image)} style={{ width: '92%' }} />}
  </AbsoluteFill>
);

const Music = ({ file, volume, total }: { file: string; volume: number; total: number }) => {
  const frame = useCurrentFrame();
  const fadeOut = interpolate(frame, [total - FPS * 1.5, total], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  return <Audio src={staticFile(file)} volume={volume * fadeOut} loop />;
};

export const Reel = (props: ReelProps) => {
  const accent = props.accent ?? '#F07A2E';
  const transitionFrames = fadeFrames(props);
  const scenes = [
    ...props.clips.map((clip) => <OffthreadVideo src={staticFile(clip.file)} volume={props.clipVolume ?? 1} />),
    ...(props.outro ? [<OutroScene outro={props.outro} accent={accent} />] : []),
  ];
  const frames = sceneFrames(props);
  return (
    <AbsoluteFill style={{ background: DARK }}>
      <TransitionSeries>
        {scenes.map((scene, i) => (
          <Fragment key={i}>
            {i > 0 && transitionFrames > 0 && (
              <TransitionSeries.Transition presentation={fade()} timing={linearTiming({ durationInFrames: transitionFrames })} />
            )}
            <TransitionSeries.Sequence durationInFrames={frames[i]}>{scene}</TransitionSeries.Sequence>
          </Fragment>
        ))}
      </TransitionSeries>
      {(props.intro ?? []).map((card, i) => (
        <Sequence key={i} from={i * CARD_FRAMES} durationInFrames={CARD_FRAMES}>
          <Card card={card} accent={accent} />
        </Sequence>
      ))}
      {props.music && <Music file={props.music.file} volume={props.music.volume ?? 0.5} total={totalFrames(props)} />}
    </AbsoluteFill>
  );
};
