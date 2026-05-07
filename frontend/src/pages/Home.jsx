import { useEffect } from 'react'
import Header from '../components/header/Header'
import { updateMeta, updateOG } from '../utils/updateOG'

export default function Home() {

  useEffect(() => {
    updateMeta({
      title: "Vastrika - Modern Fashion, Timeless Culture",
      description:
        "Shop the latest fashion trends for men, women, and kids at Vastrika. Discover clothing, accessories, beauty, and lifestyle products at the best prices.",
      keywords: "Online Fashion Store in India, Buy trendy cloths online, Affordable fashion India, Vastrika fashion",
    });

    updateOG({
      title: "Vastrika - Modern Fashion, Timeless Culture",
      description:
        "Shop the latest fashion trends for men, women, and kids at Vastrika. Discover clothing, accessories, beauty, and lifestyle products at the best prices.",
      image: "/assets/image/logo/vastrika-logo.png",
      url: "/",
    });
  }, []);

  return (
    <div>
      <Header/>
    </div>
  )
}