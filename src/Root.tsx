import { Composition } from 'remotion';
import example from '../reels/example.json';
import { FPS, Reel, type ReelProps, totalFrames } from './Reel';

export const RemotionRoot = () => (
  <Composition
    id="Reel"
    component={Reel}
    defaultProps={example as ReelProps}
    width={1080}
    height={1920}
    fps={FPS}
    durationInFrames={totalFrames(example as ReelProps)}
    calculateMetadata={({ props }) => ({ durationInFrames: totalFrames(props) })}
  />
);
