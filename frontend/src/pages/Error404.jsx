import React, { useEffect } from 'react'

import errorPage from '../assets/image/error-page.png';
import logo from '../assets/image/logo/vastrika-logo.png';
import { updateMeta, updateOG } from '../utils/updateOG';

export default function Error404() {

  useEffect(() => {
    updateMeta({
      title: "Vastrika | Page not found",
      description:
        "Oops! The page you’re looking for doesn’t exist. Continue shopping the latest fashion, clothing, and lifestyle products on Vastrika.",
    });
          
    updateOG({
      title: "Vastrika | Page not found",
      description:
        "Oops! The page you’re looking for doesn’t exist. Continue shopping the latest fashion, clothing, and lifestyle products on Vastrika.",
        image: window.location.origin + "/assets/image/logo/vastrika-logo.png",
        url: window.location.origin + "/",
    });
          
  }, []);

  return (
    <>
      <div className='app-layout'>
        <div className='main-content'>
          <div className='error-wrapper'>
            <div className='google-404'>
              <div className='google-404__left'>
                <a href={'/'}><img src={logo} alt="vastrika-logo" /></a>
                <h1 className='google-logo'>Error Page 404</h1>
                <p className='error-title'>404. That's an error.</p>

                <p className='error-desc'>
                  The requested URL was not found on this server. <br />
                  That's all we know.
                </p>
              </div>

              <div className='google-404__right'>
                <img src={errorPage} alt="404 error" />
              </div>
            </div>
          </div>
        </div>
      </div>      
    </>
  )
}