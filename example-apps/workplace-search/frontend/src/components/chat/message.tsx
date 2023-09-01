import { SourceType } from '../source_item'
import { Loader } from '../loader'

export type ChatMessageType = {
  id: number | string
  content: string
  isHuman?: boolean
  loading?: boolean
  sources?: SourceType[]
}
export const ChatMessage: React.FC<ChatMessageType> = ({
  id,
  content,
  isHuman,
  sources,
  loading,
}) => {
  const styles = {
    wrapper: {
      display: 'flex',
      width: '100%',
      justifyContent: isHuman ? 'flex-end' : 'flex-start',
      marginTop: '1.5rem',
      gap: '12px',
    },
    message: {
      padding: '12px',
      width: '400px',
      background: isHuman
        ? 'linear-gradient(180deg, #1BA9F5 0%, #52C3FF 100%)'
        : 'linear-gradient(180deg, #F7F9FC 0%, #F1F4FA 100%)',
      boxShadow: isHuman
        ? '0px 0.7px 3.4px rgba(0, 0, 0, 0.15), 0px 1.9px 8px rgba(0, 0, 0, 0.03), 0px 4.5px 16px rgba(0, 0, 0, 0.1), inset 0px 1px 1px rgba(255, 255, 255, 0.22)'
        : '0px 0.7px 3.4px rgba(0, 0, 0, 0.15), 0px 1.9px 8px rgba(0, 0, 0, 0.03), 0px 4.5px 16px rgba(0, 0, 0, 0.1), inset 0px 1px 1px #FFFFFF',
      borderRadius: '12px',
    },
    messageContent: {
      color: isHuman ? '#000000' : '#1C1E23',
      fontWeight: 500,
      textShadow: isHuman
        ? '0px 1px 0px rgba(140, 215, 255, 0.51)'
        : '0px 1px 0px #FFFFFF',
    },
    sourceList: {
      display: 'inline-flex',
      paddingLeft: '44px',
      flexDirection: 'column',
      gap: '8px',
      paddingTop: '1rem',
    },
  }
  return (
    <>
      <div style={styles.wrapper}>
        <div style={styles.message}>
          <span
            style={styles.messageContent}
            className="whitespace-pre-wrap leading-normal"
          >
            {content}
          </span>
          {loading && <Loader />}
        </div>
      </div>
      {/*{sources && (*/}
      {/*  <div className="mt-4">*/}
      {/*    <Sources sources={sources || []} />*/}
      {/*  </div>*/}
      {/*)}*/}
    </>
  )
}
