// @ts-ignore
import Image from './images/robot-avatar.png'
export const Avatar = () => {
  const styles = {
    image: {
      width: 48,
      height: 48,
      borderRadius: '14px',
      boxShadow:
        '0px 1px 5px rgba(0, 0, 0, 0.1), 0px 3.6px 13px rgba(0, 0, 0, 0.07), 0px 8.4px 23px rgba(0, 0, 0, 0.06), 0px 23px 35px rgba(0, 0, 0, 0.05), inset 0px 4px 4px rgba(255, 255, 255, 0.65)',
    },
  }
  return <img style={styles.image} src={Image} alt="Avatar Description" />
}
