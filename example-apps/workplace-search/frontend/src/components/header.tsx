// @ts-ignore
import elasticTypeMark from './images/elasticTypeMark.png'

export const Header = () => (
  <div className="flex flex-row justify-between space-x-6 px-8 py-3.5 bg-dark-ink w-full">
    <div className="pr-8 border-r border-ink">
      <a href="/">
        <img width={118} height={40} src={elasticTypeMark} />
      </a>
    </div>
  </div>
)
