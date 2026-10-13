import { Card, Empty } from '../components/ui'

export default function Planned({ title, hint }: { title: string; hint: string }) {
  return (
    <>
      <h1 className="text-xl font-bold">{title}</h1>
      <Card><Empty title={`${title} are not available yet`} hint={hint} /></Card>
    </>
  )
}
