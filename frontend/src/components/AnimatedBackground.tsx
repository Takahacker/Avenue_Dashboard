import { motion } from 'framer-motion';

const AnimatedBackground = () => {
  return (
    <div className="animated-bg">
      {/* Main gradient orbs */}
      <motion.div
        className="liquid-orb liquid-orb-1"
        animate={{
          x: [0, 100, -50, 0],
          y: [0, -80, 60, 0],
          scale: [1, 1.2, 0.9, 1],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
      <motion.div
        className="liquid-orb liquid-orb-2"
        animate={{
          x: [0, -70, 40, 0],
          y: [0, 50, -60, 0],
          scale: [1, 0.85, 1.15, 1],
        }}
        transition={{
          duration: 18,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 2,
        }}
      />
      <motion.div
        className="liquid-orb liquid-orb-3"
        animate={{
          x: [0, 60, -80, 0],
          y: [0, -40, 70, 0],
          scale: [1, 1.1, 0.95, 1],
        }}
        transition={{
          duration: 22,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 5,
        }}
      />
      
      {/* Additional subtle particles */}
      <motion.div
        className="absolute w-64 h-64 rounded-full"
        style={{
          background: 'radial-gradient(circle, hsl(39 60% 70% / 0.1), transparent 70%)',
          filter: 'blur(60px)',
          top: '40%',
          left: '60%',
        }}
        animate={{
          x: [0, 30, -30, 0],
          y: [0, -20, 20, 0],
          opacity: [0.3, 0.5, 0.3],
        }}
        transition={{
          duration: 12,
          repeat: Infinity,
          ease: "easeInOut",
        }}
      />
    </div>
  );
};

export default AnimatedBackground;
